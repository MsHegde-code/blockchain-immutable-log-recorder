import { useState } from "react";

function BlockViewer({ block }) {
  const [showLogs, setShowLogs] = useState(false);

  return (
    <div className="block-card">
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
