import { useEffect, useState } from "react";
import { fetchPagedChain, fetchValidation } from "./api";
import BlockViewer from "./components/BlockViewer";
import ChainStatus from "./components/ChainStatus";
import "./index.css";

function App() {
  const [blocks, setBlocks] = useState([]);
  const [status, setStatus] = useState(null);

  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Fetch chain validation status (once)
  useEffect(() => {
    fetchValidation().then(setStatus);
  }, []);

  // Fetch paginated blocks
  useEffect(() => {
    fetchPagedChain(page, 5).then(data => {
      setBlocks(data.blocks);
      setTotalPages(data.total_pages);
    });
  }, [page]);

  return (
  <div className="container">
    <h1>Immutable Log Blockchain</h1>

    {status && <ChainStatus status={status} />}

    {blocks.map(block => (
      <BlockViewer key={block.index} block={block} />
    ))}

    <div className="pagination">
      <button disabled={page === 1} onClick={() => setPage(page - 1)}>
        Prev
      </button>

      <span>
        Page {page} of {totalPages}
      </span>

      <button
        disabled={page === totalPages}
        onClick={() => setPage(page + 1)}
      >
        Next
      </button>
    </div>
  </div>
  );
}

export default App;
