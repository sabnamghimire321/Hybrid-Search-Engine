export function highlightSegments(text, words) {
  if (!words || words.length === 0) return [{ text, isMatch: false }];

  const cleanWords = words.filter(Boolean).map((w) => w.toLowerCase());
  if (cleanWords.length === 0) return [{ text, isMatch: false }];

  const escaped = [...cleanWords]
    .sort((a, b) => b.length - a.length)
    .map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  const pattern = new RegExp(`(${escaped.join("|")})`, "gi");

  const parts = text.split(pattern);
  return parts.map((part) => ({
    text: part,
    isMatch: cleanWords.includes(part.toLowerCase()),
  }));
}