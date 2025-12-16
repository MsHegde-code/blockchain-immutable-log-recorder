import hashlib
import json
from datetime import datetime

class Block:
    def __init__(self, index, logs, previous_hash):
        self.index = index
        self.timestamp = datetime.utcnow().isoformat()
        self.logs = logs
        self.previous_hash = previous_hash
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "logs": self.logs,
            "previous_hash": self.previous_hash
        }, sort_keys=True)

        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "logs": self.logs,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }
