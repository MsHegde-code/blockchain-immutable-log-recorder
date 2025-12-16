function ChainStatus({ status }) {
  return (
    <div
      className="status-box"
      style={{
        backgroundColor: status.valid ? "#dcfce7" : "#fee2e2",
        color: status.valid ? "#166534" : "#7f1d1d"
      }}
    >
      Status: {status.message}
      {!status.valid && (
        <div>Broken at block #{status.broken_block}</div>
      )}
    </div>
  );
}

export default ChainStatus;
