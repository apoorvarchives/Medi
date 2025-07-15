import rsa
from block import Block

class Server:
    def __init__(self, chain, min_accuracy=0.5):
        self.chain = chain
        self.min_accuracy = min_accuracy  # threshold to reject bad model blocks

    def verify_signature(self, block):
        try:
            if not block.signature or not block.public_key:
                return False

            pubkey = rsa.PublicKey.load_pkcs1(block.public_key.encode())
            rsa.verify(block.hash.encode(), bytes.fromhex(block.signature), pubkey)
            return True
        except Exception as e:
            print(f"[!] Signature verification failed for Miner {block.miner}: {e}")
            return False

    def receive_blocks(self, mined_blocks, miners):
        if not mined_blocks:
            print("[!] No blocks to process.")
            return

        # Winner = first valid block
        block = mined_blocks[0]

        if not self.verify_signature(block):
            print(f"[⛔] Block from Miner {block.miner} rejected: invalid signature.")
            return

        # Optional: validate model hash/accuracy if included
        if "accuracy" in block.access_logs[0]:
            acc = block.access_logs[0]["accuracy"]
            if acc < self.min_accuracy:
                print(f"[⛔] Block from Miner {block.miner} rejected: accuracy too low ({acc:.2f}%).")
                return

        print(f"\n[🏁] Miner {block.miner} wins the PoW race with Block #{block.index}!")

        # Broadcast to all miners
        for miner in miners:
            miner.chain.append(block)  # or miner.chain.add_block_object(block) if using EHRChain
            print(f"[✔️] Miner {miner.miner_id} validated and appended Block #{block.index}.")

        # Add to central chain view
        self.chain.add_block_object(block)
        print(f"[✓] Global model updated using block from {block.miner}.")
