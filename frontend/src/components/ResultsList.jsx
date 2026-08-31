import ResultCard from "./ResultCard";

export default function ResultsList({ results, queryWords, loading, error }) {
  if (loading) return <p className="status">Searching...</p>;
  if (error) return <p className="status error">{error}</p>;
  if (results.length === 0) return <p className="status">No results found.</p>;

  return (
    <div className="results-list">
      {results.map((r) => (
        <ResultCard key={r.doc_id} result={r} queryWords={queryWords} />
      ))}
    </div>
  );
}