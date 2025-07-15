# --------------------------- ehr_main.py ---------------------------
import yaml
import time
import random
import hashlib
import os
import json
import torch
from faker import Faker
from concurrent.futures import ThreadPoolExecutor, as_completed
from torch.utils.data import DataLoader, TensorDataset

from ehr_chain import EHRChain
from fl_trainer import FLTrainer
from miner import Miner
from server import Server
from fl_node import FLNode
from visualize import visualize_chain  # 🔁 we'll generate this too

fake = Faker()

def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)

def generate_patient_record():
    return {
        "patient_id": fake.unique.lexify(text='P????'),
        "name": fake.name(),
        "age": random.randint(20, 85),
        "gender": random.choice(["Male", "Female"]),
        "record_type": random.choice(["MRI", "Blood Test", "CT Scan", "Prescription"]),
        "vitals": f"HR {random.randint(60, 100)} bpm"
    }

def convert_to_tensor(patient):
    age = patient['age'] / 100.0
    gender = 1.0 if patient['gender'] == 'Male' else 0.0
    hr = int(patient['vitals'].split()[1]) / 200.0
    record_map = {"MRI": 0.0, "Blood Test": 0.33, "CT Scan": 0.66, "Prescription": 1.0}
    record_type = record_map[patient['record_type']]
    label = 1 if patient['age'] > 60 and hr * 200 > 90 else 0
    x = torch.tensor([age, gender, hr, record_type], dtype=torch.float32)
    y = torch.tensor(label)
    return x, y

def log_patient_record(patient):
    os.makedirs("patient_records", exist_ok=True)
    pid = patient["patient_id"]
    filepath = os.path.join("patient_records", f"{pid}.json")

    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            history = json.load(f)
    else:
        history = []

    history.append(patient)

    with open(filepath, "w") as f:
        json.dump(history, f, indent=2)

if __name__ == '__main__':
    config = load_config()
    chain = EHRChain()
    server = Server(chain)

    num_rounds = config.get('num_rounds', 5)
    lr = config.get('lr', 0.01)
    clients_per_round = config.get('clients_per_round', 5)
    block_size = config.get('block_size', 5)
    t_wait = config.get('t_wait', 5)
    difficulty = config.get('difficulty', 2)

    nodes = list(config['nodes'].keys())


    miners = []
    for node_id in nodes:
      miners.append(Miner(
        miner_id=node_id,
        block_size=block_size,
        timeout=t_wait,
        difficulty=difficulty,
        is_malicious=False  # No malicious miner
    ))


    hospital_ids = [m.miner_id for m in miners]

    for epoch in range(1, num_rounds + 1):
        print(f"\n====================== EPOCH {epoch} ======================")
        hospital_data = {hid: [] for hid in hospital_ids}

        # Patient generation + broadcasting
        for hid in hospital_ids:
            for _ in range(clients_per_round):
                patient = generate_patient_record()
                log_patient_record(patient)
                x, y = convert_to_tensor(patient)
                hospital_data[hid].append((x, y))

                access_log = {
                    "record_hash": hashlib.sha256(str(patient).encode()).hexdigest(),
                    "accessed_by": "FederatedModel",
                    "timestamp": time.time(),
                    "approved_by_patient": True,
                    "contributor": hid
                }

                for miner in miners:
                    miner.add_update(patient, access_log)

                print(f"[+] Patient {patient['name']} assigned to {hid}")

        # Prepare data
        node_data = {}
        for hid, data_points in hospital_data.items():
            X, Y = zip(*data_points)
            dataset = TensorDataset(torch.stack(X), torch.tensor(Y))
            node_data[hid] = DataLoader(dataset, batch_size=4, shuffle=True)

        test_loader = DataLoader(TensorDataset(
            torch.stack([p[0] for points in hospital_data.values() for p in points]),
            torch.tensor([p[1] for points in hospital_data.values() for p in points])
        ), batch_size=4)

        fl_trainer = FLTrainer(node_data_dict=node_data, test_loader=test_loader)
        global_model, model_hash, accuracy, contributors, local_scores = fl_trainer.run_round(local_epochs=2, lr=lr)

        print("Local Model Accuracies:")
        for cid, acc in local_scores.items():
            print(f"  - {cid}: {acc:.2f}%")

        previous_hash = chain.get_last_block().hash
        index = chain.get_last_block().index + 1

        print("\n[🔁] Starting parallel PoW race...")
        with ThreadPoolExecutor(max_workers=len(miners)) as executor:
            futures = {
                executor.submit(miner.mine_block, previous_hash, index, model_hash): miner
                for miner in miners if miner.is_ready_to_mine()
            }

            winner_block = None
            mined_blocks = []

            for future in as_completed(futures):
                mined_block = future.result()
                if mined_block and mined_block.hash.startswith("0" * difficulty):
                    winner_block = mined_block
                    mined_blocks.append(mined_block)
                    break

        for miner in miners:
            miner.reset_candidate()

        if winner_block:
            # Add accuracy to access logs for server check
            winner_block.access_logs.append({
                "event": "Model Aggregated",
                "round": epoch,
                "accuracy": accuracy
            })
            server.receive_blocks(mined_blocks, miners)

            # 🔍 Visualize chain after each round
            visualize_chain(chain, round_num=epoch)
        else:
            print("[!] No valid block mined this round.")

    print("\n[✓] Federated Training + Blockchain Logging Complete. Saved to ehr_chain.json")
