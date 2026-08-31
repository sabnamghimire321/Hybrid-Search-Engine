const SOURCE_TYPES = [
  { value: null, label: "All" },
  { value: "txt", label: "Text" },
  { value: "pdf", label: "PDF" },
  { value: "html", label: "HTML" },
  { value: "markdown", label: "Markdown" },
];

export default function Filters({ selected, onChange }) {
  return (
    <div className="filters">
      {SOURCE_TYPES.map(({ value, label }) => (
        <button
          key={label}
          type="button"
          className={selected === value ? "filter active" : "filter"}
          onClick={() => onChange(value)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}