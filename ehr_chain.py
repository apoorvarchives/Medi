# --------------------------- ehr_chain.py ---------------------------
import json
import os
from block import Block

class EHRChain:
    def __init__(self):
        self.chain = []
        self.load_chain()

    def create_genesis_block(self):
        genesis_block = Block(
            index=0,
            records=[],
            access_logs=[],
            previous_hash="0",
            miner="genesis",
            model_hash="0" * 64,
            difficulty=2
        )
        self.chain.append(genesis_block)

    def add_block_object(self, block):
        self.chain.append(block)
        self.save_chain()

    def get_last_block(self):
        return self.chain[-1]

    def save_chain(self):
        data = [block.to_dict() for block in self.chain]
        with open("ehr_chain.json", "w") as f:
            json.dump(data, f, indent=2)

    def load_chain(self):
        if os.path.exists("ehr_chain.json"):
            with open("ehr_chain.json", "r") as f:
                chain_data = json.load(f)
                for block_data in chain_data:
                    block = Block.from_dict(block_data)
                    self.chain.append(block)
        else:
            self.create_genesis_block()