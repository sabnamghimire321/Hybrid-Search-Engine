import { useState } from "react";
import { highlightSegments } from "../highlight";

export default function ResultCard({ result, queryWords }) {
  const [showExplanation, setShowExplanation] = useState(false);
  const segments = highlightSegments(result.snippet, queryWords);

  const breakdown = Object.entries(result.score_breakdown || {}).sort(
    (a, b) => b[1] - a[1]
  );
  const maxTermScore = Math.max(1, ...breakdown.map(([, score]) => score));

  return (
    <div className="result-card">
      <div className="result-header">
        <h3>{result.title}</h3>
        <span className="result-score">{result.score.toFixed(2)}</span>
      </div>

      <div className="result-meta">
        <span className="badge">{result.source_type}</span>
        <span className="path">{result.path}</span>
      </div>

      <p className="snippet">
        {segments.map((seg, i) =>
          seg.isMatch ? (
            <mark key={i}>{seg.text}</mark>
          ) : (
            <span key={i}>{seg.text}</span>
          )
        )}
      </p>

      <button
        type="button"
        className="explain-toggle"
        onClick={() => setShowExplanation(!showExplanation)}
      >
        {showExplanation ? "Hide explanation" : "Why did this rank here?"}
      </button>

      {showExplanation && (
        <div className="explanation">
          {breakdown.map(([term, score]) => (
            <div key={term} className="explanation-row">
              <span className="term">{term}</span>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{ width: `${(score / maxTermScore) * 100}%` }}
                />
              </div>
              <span className="term-score">{score.toFixed(3)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}