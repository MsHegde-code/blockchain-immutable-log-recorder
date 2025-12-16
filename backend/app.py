from flask import Flask, jsonify
from flask_cors import CORS
from flask import request

from blockchain.blockchain import Blockchain
from blockchain.log_importer import read_jsonl, group_logs
from blockchain.validator import validate_chain

app = Flask(__name__)
CORS(app)

CHAIN_PATH = "storage/chain.json"
LOG_FILES = [
    "data/security.jsonl",
    "data/firewall.jsonl",
    "data/system.jsonl"
]

# Limiting to 1000 blocks for demo
blockchain = Blockchain(max_blocks=1000)

for log_file in LOG_FILES:
    logs = read_jsonl(log_file)
    for group in group_logs(logs, block_size=5):
        blockchain.add_block(group)

blockchain.save(CHAIN_PATH)

@app.route("/api/chain", methods=["GET"])
def get_chain():
    return jsonify(blockchain.to_list())

@app.route("/api/validate", methods=["GET"])
def validate():
    chain = blockchain.to_list()
    valid, index, message = validate_chain(chain)
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
