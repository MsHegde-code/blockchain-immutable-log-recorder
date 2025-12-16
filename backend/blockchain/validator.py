import json
import hashlib


def validate_chain(chain):
    """
    In-memory validation (optional / legacy)
    """
    for i in range(1, len(chain)):
        current = chain[i]
        previous = chain[i - 1]

        recomputed = hashlib.sha256(
            json.dumps(
                {
                    "index": current["index"],
                    "timestamp": current["timestamp"],
                    "logs": current["logs"],
                    "previous_hash": current["previous_hash"],
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()

        if current["hash"] != recomputed:
            return False, i, "Hash mismatch"

        if current["previous_hash"] != previous["hash"]:
            return False, i, "Broken previous-hash link"

    return True, None, "Chain intact"


def validate_chain_from_file(chain_file_path):
    """
    Disk-based validation (CORRECT for tamper detection)
    """

    with open(chain_file_path, "r") as f:
        chain = json.load(f)

    for i in range(1, len(chain)):
        current = chain[i]
        previous = chain[i - 1]

        recomputed_hash = hashlib.sha256(
            json.dumps(
                {
                    "index": current["index"],
                    "timestamp": current["timestamp"],
                    "logs": current["logs"],
                    "previous_hash": current["previous_hash"],
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()

        if current["hash"] != recomputed_hash:
            return False, i, "Hash mismatch detected"

        if current["previous_hash"] != previous["hash"]:
            return False, i, "Broken previous-hash link"

    return True, None, "Chain intact"
