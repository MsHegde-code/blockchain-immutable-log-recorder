import os
import json
from datetime import datetime
from utils.evtx_parser import parse_evtx

# NOTE:
# This is a generic, demo-safe parser.
# Real EVTX parsing can be added later using python-evtx.

SUPPORTED_EXTENSIONS = [".log", ".txt", ".evtx"]


def convert_logs_to_jsonl(input_dir, output_dir):
    """
    Scans input_dir for raw log files (.log/.txt/.evtx)
    Converts them to .jsonl and saves in output_dir
    """

    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        name, ext = os.path.splitext(filename)

        if ext.lower() not in SUPPORTED_EXTENSIONS:
            continue

        jsonl_path = os.path.join(output_dir, f"{name}.jsonl")

        # Avoid reconversion
        if os.path.exists(jsonl_path):
            continue

        if ext.lower() == ".evtx":
            print(f"[+] Converting {filename} (EVTX) → {name}.jsonl")
            with open(jsonl_path, "w") as fout:
                for entry in parse_evtx(file_path):
                     log_entry = {
                        "timestamp": entry["timestamp"],
                        "source_file": filename,
                        "message": entry["message"]
                    }
                     fout.write(json.dumps(log_entry) + "\n")
        
        else:
            # TEXT / LOG conversion
            print(f"[+] Converting {filename} → {name}.jsonl")

            with open(file_path, "r", errors="ignore") as fin, \
                 open(jsonl_path, "w") as fout:

                for line in fin:
                    line = line.strip()
                    if not line:
                        continue

                    log_entry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "source_file": filename,
                        "message": line
                    }

                    fout.write(json.dumps(log_entry) + "\n")
