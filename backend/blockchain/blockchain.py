import json
from .block import Block

class Blockchain:
    def __init__(self, max_blocks=1000):
        self.chain = []
        self.max_blocks = max_blocks
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(0, ["Genesis Block"], "0")
        self.chain.append(genesis)

    def add_block(self, logs):
        if len(self.chain) >= self.max_blocks:
            return  # stop adding more blocks
        
        prev_block = self.chain[-1]
        block = Block(len(self.chain), logs, prev_block.hash)
        self.chain.append(block)

    def to_list(self):
        return [block.to_dict() for block in self.chain]

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.to_list(), f, indent=2)
