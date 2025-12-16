import hashlib
import json

def validate_chain(chain):
    for i in range(1, len(chain)):
        current = chain[i]
        previous = chain[i - 1]

        recomputed = hashlib.sha256(json.dumps({
            "index": current["index"],
            "timestamp": current["timestamp"],
            "logs": current["logs"],
            "previous_hash": current["previous_hash"]
        }, sort_keys=True).encode()).hexdigest()

        if current["hash"] != recomputed:
            return False, i, "Hash mismatch"

        if current["previous_hash"] != previous["hash"]:
            return False, i, "Broken previous-hash link"

    return True, None, "Chain intact"
