const BASE_URL = "/api";

export async function search(query, { sourceType = null, topK = 10 } = {}) {
  const params = new URLSearchParams({ q: query, top_k: String(topK) });
  if (sourceType) params.set("source_type", sourceType);

  const response = await fetch(`${BASE_URL}/search?${params}`);
  if (!response.ok) {
    throw new Error(`Search failed: ${response.status}`);
  }
  return response.json();
}

export async function suggest(prefix, limit = 8) {
  if (!prefix) return { suggestions: [] };

  const params = new URLSearchParams({ prefix, limit: String(limit) });
  const response = await fetch(`${BASE_URL}/suggest?${params}`);
  if (!response.ok) {
    return { suggestions: [] };
  }
  return response.json();
}

export async function fetchStats() {
  const response = await fetch(`${BASE_URL}/stats`);
  if (!response.ok) {
    throw new Error(`Stats failed: ${response.status}`);
  }
  return response.json();
}