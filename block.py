import hashlib
import json
import time

class Block:
    def __init__(self, index, records, access_logs, previous_hash, miner, model_hash, difficulty=2):
        self.index = index
        self.records = records
        self.access_logs = access_logs
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.nonce = 0
        self.miner = miner
        self.model_hash = model_hash
        self.difficulty = difficulty
        self.signature = None
        self.public_key = None
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_data = {
            "index": self.index,
            "records": self.records,
            "access_logs": self.access_logs,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "miner": self.miner,
            "model_hash": self.model_hash
        }
        return hashlib.sha256(json.dumps(block_data, sort_keys=True).encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "records": self.records,
            "access_logs": self.access_logs,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "miner": self.miner,
            "model_hash": self.model_hash,
            "difficulty": self.difficulty,
            "hash": self.hash,
            "signature": self.signature,
            "public_key": self.public_key
        }

    @staticmethod
    def from_dict(data):
        block = Block(
            index=data["index"],
            records=data["records"],
            access_logs=data["access_logs"],
            previous_hash=data["previous_hash"],
            miner=data["miner"],
            model_hash=data["model_hash"],
            difficulty=data.get("difficulty", 2)
        )
        block.timestamp = data["timestamp"]
        block.nonce = data["nonce"]
        block.hash = data["hash"]
        block.signature = data.get("signature")
        block.public_key = data.get("public_key")
        return block
