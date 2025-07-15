# --------------------------- miner.py ---------------------------
import hashlib
import json
import time
import rsa
from block import Block

class Miner:
    def __init__(self, miner_id, block_size, timeout, difficulty, is_malicious=False):
        self.miner_id = miner_id
        self.block_size = block_size
        self.timeout = timeout
        self.difficulty = difficulty
        self.is_malicious = False  # Clean mode always
        self.public_key, self.private_key = rsa.newkeys(512)

        self.candidate_block = {
            "records": [],
            "access_logs": [],
            "model_hash": None
        }
        self.chain = []

    def add_update(self, patient, access_log):
        self.candidate_block["records"].append(patient)
        self.candidate_block["access_logs"].append(access_log)

    def is_ready_to_mine(self):
        return len(self.candidate_block["records"]) >= self.block_size

    def mine_block(self, previous_hash, index, model_hash):
        self.candidate_block["model_hash"] = model_hash

        block = Block(
            index=index,
            records=self.candidate_block["records"],
            access_logs=self.candidate_block["access_logs"],
            previous_hash=previous_hash,
            miner=self.miner_id,
            model_hash=model_hash,
            difficulty=self.difficulty
        )

        start = time.time()
        while not block.hash.startswith("0" * self.difficulty):
            block.nonce += 1
            block.hash = block.compute_hash()
        end = time.time()

        # Sign the block hash
        signature = rsa.sign(block.hash.encode(), self.private_key, 'SHA-256')
        block.signature = signature.hex()
        block.public_key = self.public_key.save_pkcs1().decode()

        print(f"[⛏️] Miner {self.miner_id} mined a block in {round(end - start, 2)}s.")
        return block

    def reset_candidate(self):
        self.candidate_block = {
            "records": [],
            "access_logs": [],
            "model_hash": None
        }
