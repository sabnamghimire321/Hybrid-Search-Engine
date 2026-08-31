import { useEffect, useRef, useState } from "react";
import { suggest } from "../api";

export default function SearchBar({ onSearch }) {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const debounceRef = useRef(null);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);

    const lastWord = query.trim().split(/\s+/).pop();
    if (!lastWord || lastWord.length < 2) {
      setSuggestions([]);
      return;
    }

    debounceRef.current = setTimeout(async () => {
      const data = await suggest(lastWord);
      setSuggestions(data.suggestions || []);
    }, 200);

    return () => clearTimeout(debounceRef.current);
  }, [query]);

  function handleSubmit(e) {
    e.preventDefault();
    setShowSuggestions(false);
    onSearch(query);
  }

  function applySuggestion(word) {
    const words = query.trim().split(/\s+/);
    words[words.length - 1] = word;
    setQuery(words.join(" ") + " ");
    setShowSuggestions(false);
  }

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <div className="search-input-wrapper">
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setShowSuggestions(true);
          }}
          placeholder="Search your documents..."
          autoFocus
        />
        <button type="submit">Search</button>
      </div>
      {showSuggestions && suggestions.length > 0 && (
        <ul className="suggestions">
          {suggestions.map((s) => (
            <li key={s} onMouseDown={() => applySuggestion(s)}>
              {s}
            </li>
          ))}
        </ul>
      )}
    </form>
  );
}