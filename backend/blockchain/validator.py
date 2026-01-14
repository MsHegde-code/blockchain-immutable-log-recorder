import json
import hashlib
import os
from utils.evtx_parser import parse_evtx


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


def validate_chain_against_raw_files(chain_file_path, raw_log_dir):
    """
    Validates that the logs stored in the chain match the actual content
    of the raw log files in raw_log_dir.
    """
    try:
        with open(chain_file_path, "r") as f:
            chain = json.load(f)
    except FileNotFoundError:
        return False, 0, "Chain file not found"

    # 1. Collect all logs from the chain, grouped by source file
    chain_logs_by_file = {}
    
    # We also keep track of which block each log came from for better error reporting
    # structure: filename -> list of (log_entry, block_index)
    for block in chain:
        if block["index"] == 0: continue # Skip genesis
        for log in block["logs"]:
            fname = log.get("source_file")
            if not fname: continue
            
            if fname not in chain_logs_by_file:
                chain_logs_by_file[fname] = []
            chain_logs_by_file[fname].append((log, block["index"]))

    print(f"DEBUG: Found {len(chain)} blocks. Keys: {list(chain_logs_by_file.keys())}")

    # 2. Iterate each file and compare
    for filename, chained_entries in chain_logs_by_file.items():
        file_path = os.path.join(raw_log_dir, filename)
        
        if not os.path.exists(file_path):
            first_block_idx = chained_entries[0][1]
            return False, first_block_idx, f"Source file '{filename}' was deleted or moved."

        # Read raw file entries
        raw_entries = []
        try:
            if filename.lower().endswith(".evtx"):
                for entry in parse_evtx(file_path):
                    raw_entries.append(entry["message"])
            else:
                # Text/Log file
                with open(file_path, "r", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            raw_entries.append(line)
        except Exception as e:
            return False, 0, f"Error reading raw file '{filename}': {str(e)}"

        # 3. Compare Chain Sequence vs Raw Sequence
        # We only check up to the length of the chain. 
        # (New logs might have been appended to raw file which are not yet in chain -> OK)
        
        if len(raw_entries) < len(chained_entries):
             # Raw file is shorter than what we have in chain -> Data deletions!
             missing_count = len(chained_entries) - len(raw_entries)
             # The first missing one is at index len(raw_entries)
             # But wait, we should find exactly where it deviates.
             # Actually, if it's shorter, the first missing one is the problem.
             
             # Let's find the first deviation or just report truncation
             # Check the ones that exist first
             for i in range(len(raw_entries)):
                 chain_msg = chained_entries[i][0]["message"]
                 raw_msg = raw_entries[i]
                 if chain_msg != raw_msg:
                     block_idx = chained_entries[i][1]
                     return False, block_idx, f"Mismatch in '{filename}' at line {i+1}. Chain has '{chain_msg[:30]}...', File has '{raw_msg[:30]}...'"
             
             # If all match, then it's a truncation
             first_missing_idx = len(raw_entries)
             block_idx = chained_entries[first_missing_idx][1]
             return False, block_idx, f"File '{filename}' is missing logs. Expected {len(chained_entries)} chained entries, found {len(raw_entries)}."

        # If raw_entries >= chained_entries, check the prefix
        for i, (chain_data, block_idx) in enumerate(chained_entries):
            chain_msg = chain_data["message"]
            raw_msg = raw_entries[i]
            
            # Simple string equality
            if chain_msg != raw_msg:
                return False, block_idx, f"Tamper Detected in '{filename}' at line {i+1} (Block {block_idx})."

    # If all file checks pass, we also run the cryptographic check
    is_valid, bad_idx, msg = validate_chain_from_file(chain_file_path)
    if not is_valid:
        return False, bad_idx, msg

    return True, None, "Chain and Raw Files Intact"
