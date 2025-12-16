import json

def read_jsonl(path):
    logs = []
    with open(path, "r") as f:
        for line in f:
            logs.append(json.loads(line.strip()))
    return logs

def group_logs(logs, block_size=5):
    for i in range(0, len(logs), block_size):
        yield logs[i:i + block_size]
