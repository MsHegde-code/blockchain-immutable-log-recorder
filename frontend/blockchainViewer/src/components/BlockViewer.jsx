import { useState } from "react";

function BlockViewer({ block, brokenBlock, isChainValid }) {
  const [showLogs, setShowLogs] = useState(false);

  // A block is considered tampered if:
  // chain is invalid AND this block index >= broken block
  const isTampered =
    isChainValid === false && block.index >= brokenBlock;

  return (
    <div className={`block-card ${isTampered ? "tampered-block" : ""}`}>
      <h3>Block #{block.index}</h3>

      <p><strong>Hash:</strong></p>
      <code>{block.hash}</code>

      <p><strong>Previous Hash:</strong></p>
      <code>{block.previous_hash}</code>

      <button onClick={() => setShowLogs(!showLogs)}>
        {showLogs ? "Hide Log" : "View Log"}
      </button>

      {showLogs && (
        <pre className="log-box">
          {JSON.stringify(block.logs, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default BlockViewer;
