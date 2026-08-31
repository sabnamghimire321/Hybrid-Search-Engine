import { useState } from "react";
import SearchBar from "./components/SearchBar";
import Filters from "./components/Filters";
import ResultsList from "./components/ResultsList";
import { search as searchApi } from "./api";

export default function App() {
  const [results, setResults] = useState([]);
  const [queryWords, setQueryWords] = useState([]);
  const [sourceType, setSourceType] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [lastQuery, setLastQuery] = useState("");

  async function runSearch(query, overrideSourceType = sourceType) {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setHasSearched(true);
    setLastQuery(query);
    setQueryWords(query.split(/\s+/).filter(Boolean));

    try {
      const data = await searchApi(query, { sourceType: overrideSourceType });
      setResults(data.results);
    } catch (err) {
      setError("Something went wrong. Is the backend running?");
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  function handleFilterChange(newType) {
    setSourceType(newType);
    if (lastQuery) runSearch(lastQuery, newType);
  }

  return (
    <div className="app">
      <header>
        <h1>Hybrid Search Engine</h1>
        <p className="subtitle">
          Custom-built inverted index, BM25 ranking, and hybrid semantic search
        </p>
      </header>

      <SearchBar onSearch={(q) => runSearch(q)} />

      {hasSearched && <Filters selected={sourceType} onChange={handleFilterChange} />}

      {hasSearched && (
        <ResultsList
          results={results}
          queryWords={queryWords}
          loading={loading}
          error={error}
        />
      )}
    </div>
  );
}