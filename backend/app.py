import os
import json

from flask import Flask, jsonify, request
from flask_cors import CORS

from blockchain.blockchain import Blockchain
from blockchain.block import Block
from blockchain.log_importer import read_jsonl, group_logs
from blockchain.validator import validate_chain_from_file
from utils.log_converter import convert_logs_to_jsonl

app = Flask(__name__)
CORS(app)

CHAIN_PATH = "storage/chain.json"
RAW_LOG_DIR = "data/logs"
JSONL_DIR = "data"

convert_logs_to_jsonl(RAW_LOG_DIR, JSONL_DIR)

JSONL_FILES = [
    os.path.join(JSONL_DIR, f)
    for f in os.listdir(JSONL_DIR)
    if f.endswith(".jsonl")
]

blockchain = Blockchain(max_blocks=1000)
blockchain.chain = []

if os.path.exists(CHAIN_PATH):
    # IMMUTABLE MODE: Load existing chain
    with open(CHAIN_PATH, "r") as f:
        chain_data = json.load(f)

    for b in chain_data:
        block = Block(
            index=b["index"],
            logs=b["logs"],
            previous_hash=b["previous_hash"]
        )
        block.timestamp = b["timestamp"]
        block.hash = b["hash"]
        blockchain.chain.append(block)

else:
    # CREATE CHAIN ONCE
    blockchain.create_genesis_block()

    for log_file in JSONL_FILES:
        logs = read_jsonl(log_file)
        for group in group_logs(logs, block_size=5):
            blockchain.add_block(group)

    blockchain.save(CHAIN_PATH)

# --------------------------------------------------
# API Endpoints
# --------------------------------------------------

@app.route("/api/validate", methods=["GET"])
def validate():
    valid, index, message = validate_chain_from_file(CHAIN_PATH)
    return jsonify({
        "valid": valid,
        "broken_block": index,
        "message": message
    })


@app.route("/api/chain/paged", methods=["GET"])
def get_chain_paged():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("size", 5))

    chain = blockchain.to_list()
    total_blocks = len(chain)
    total_pages = (total_blocks + page_size - 1) // page_size

    start = (page - 1) * page_size
    end = start + page_size

    return jsonify({
        "blocks": chain[start:end],
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "total_blocks": total_blocks
    })


if __name__ == "__main__":
    app.run(debug=True)
