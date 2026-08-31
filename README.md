# Hybrid Search Engine
A search engine built from the ground up, without Elasticsearch, Lucene, or any other retrieval framework doing the heavy lifting. Every core piece the inverted index, the ranking algorithms, the data structures, the crawler, the vector search, even the rate limiter is hand-written, so the goal was never just "make search work," it was to understand *why* it works.

The project starts with classical information retrieval (tokenization, inverted indexes, BM25) and builds up to a hybrid engine that blends keyword search with semantic vector search, wrapped in a FastAPI backend and a React frontend.

## What it actually does

- Loads and indexes `.txt`, `.pdf`, `.html`, and `.md` files
- Supports boolean queries (`AND` / `OR` / `NOT`) and exact `"phrase search"`
- Ranks results with BM25, with TF-IDF and cosine similarity available as alternatives
- Combines keyword relevance with semantic embedding similarity for hybrid retrieval
- Includes a retrieval-augmented generation (RAG) layer, with an extractive answer generator that needs no API key and an optional Claude-backed generator for full answers
- Crawls a small site graph with robots.txt compliance, URL normalization, and duplicate detection
- Persists the index to disk with a custom binary format and memory-mapped reads
- Serves everything through a FastAPI API with API-key auth, per-endpoint rate limiting, request logging, and query analytics
- Ships a React search UI with result highlighting and source-type filters

## Why build it from scratch

Most people never see what's inside a search engine you send a query to Elasticsearch and results come back. That's great for shipping products, but it hides the actual engineering: how an inverted index is structured, why BM25 beats raw TF-IDF, what a memory-mapped file buys you over a Python dict, why threading helps I/O-bound crawling but does nothing for CPU-bound indexing.

So this project takes the slower path: implement the real thing first, benchmark it, understand where it breaks, and only then think about what a production system like Lucene does differently. The `docs/benchmarks` and `docs/research` folders exist for exactly this measured comparisons instead of assumptions.

## Architecture

```
 React Frontend  (search box, filters, result highlighting)
        │  HTTP
        ▼
 FastAPI API      auth · rate limiting · request logging · analytics
        │
        ▼
 Query Engine     boolean / phrase parsing → BM25, TF-IDF, or hybrid
                  (keyword + embedding) ranking
        │
        ▼
 Index Layer      inverted index + vector index, persisted to a custom
                  binary format, read back via memory-mapped files
        ▲
        │  built from
 ┌──────┴───────────────┬────────────────────┬──────────────────────┐
 Document Loaders        Preprocessing         Web Crawler
 (txt / pdf / html / md)  Pipeline               robots.txt, URL
                          tokenize → stopwords    frontier, scheduler
                          → stemming

 all of the above run on hand-rolled data structures and algorithms:
 trie, heap, hash table, LRU cache, graph, binary search, sorting, etc.
```

Query flow, end to end:

1. A request hits the FastAPI layer, where it passes through rate limiting and (for write/analytics endpoints) API key auth.
2. The query string is parsed for `AND` / `OR` / `NOT` operators and quoted phrases, and resolved against the inverted index to get a candidate document set.
3. Candidates are scored — by BM25 alone, or by the hybrid ranker, which also embeds the query, compares it against stored document vectors with cosine similarity, and blends the two normalized scores.
4. Results are trimmed to `top_k`, given a highlighted snippet, and returned as JSON. The query itself is logged for analytics.

On the ingestion side, a document goes: raw file → loader (extracts plain text) → preprocessing pipeline (tokenize, strip stopwords, stem) → inverted index (postings lists) and, optionally, an embedding provider → vector index. The crawler feeds the same pipeline for web-sourced documents, respecting robots.txt and de-duplicating URLs via the custom frontier and scheduler.

For a written breakdown per module, see [`docs/architecture`](docs/architecture); measured results (BM25 vs TF-IDF quality, threading vs multiprocessing, indexing throughput) live in [`docs/benchmarks`](docs/benchmarks).

## Project layout

```
src/search_engine/
├── core/               # Document model, loaders, preprocessing, query engine, inverted index
├── datastructures/      # Hash table, trie, heap, priority queue, LRU cache, graph — all hand-rolled
├── algorithms/          # Binary search, sorting, tree/graph traversal, edit distance, string matching
├── ranking/              # TF-IDF, BM25, cosine similarity, PageRank, evaluation metrics
├── storage/              # Binary serialization, persistent index, memory-mapped store, incremental updates
├── performance/          # Profiling, parallel indexing, async search, benchmarking harness
├── crawler/              # Breadth-first crawler, robots.txt parser, URL frontier, scheduler
├── semantic/             # Embedding providers, vector index, hybrid search, RAG answer generation
├── api/                  # FastAPI app, routes, auth, rate limiting, query analytics
├── observability/        # Structured logging, request middleware
└── cli/                  # Interactive command-line search

frontend/                # React + Vite search UI
tests/                   # Unit tests per module, plus end-to-end integration tests
benchmarks/              # Scripts that produce the numbers in docs/benchmarks
docs/                    # Architecture notes, benchmark write-ups, research
docker/                  # Container build for the API
```

## Getting started

Clone the repo and set up a virtual environment:

```bash
git clone <repository-url>
cd hybrid-search-engine
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### Command-line search

Index a folder and drop into an interactive search prompt:

```bash
python -m search_engine.cli.main ./data/raw
```

```
Indexing documents in ./data/raw ...
Indexed 42 documents (1,203 unique terms).

Query syntax: bare words = AND, "quoted phrase" = exact phrase, AND/OR/NOT supported. Type "exit" to quit.

search> distributed systems AND "consensus algorithm"
  3 result(s):
    [7] Raft Explained  (./data/raw/raft.md)
    ...
```

### Running the API

```bash
uvicorn search_engine.api.main:app --reload
```

This starts the FastAPI server on `http://localhost:8000` with interactive docs at `/docs`. Key endpoints:

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/health` | GET | — | Liveness check |
| `/search` | GET | — | Ranked search (`q`, `source_type`, `top_k`) |
| `/suggest` | GET | — | Autocomplete from the indexed vocabulary (`prefix`, `limit`) |
| `/stats` | GET | — | Document count and vocabulary size |
| `/index` | POST | API key | Index a directory of documents |
| `/history` | GET | API key | Query history for the calling API key |
| `/analytics` | GET | API key | Aggregate query analytics across all users |

Set `SEARCH_ENGINE_API_KEYS` (comma-separated) to configure valid API keys; it defaults to a single dev key so the server runs out of the box.

### Running the frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server proxies API calls to `http://localhost:8000`, so run the backend alongside it.

### Docker

```bash
docker build -t hybrid-search-engine -f docker/Dockerfile .
docker run -p 8000:8000 hybrid-search-engine
```

### Running the tests

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

56 test files cover the data structures, algorithms, ranking, storage, crawler, semantic search, and API layers individually, plus an end-to-end integration test that exercises indexing through search through the API.

## Design principles

A few things this project tries to hold itself to:

- **Build before importing.** Every core component is implemented from first principles before reaching for a production library.
- **Optional stays optional.** `sentence-transformers` and `anthropic` are lazily imported and guarded — the engine runs fully without either, using a hash-based embedding provider and an extractive answer generator instead.
- **Measure, don't assume.** Claims about performance (BM25 vs TF-IDF, threading vs multiprocessing, indexing throughput) are backed by numbers in `docs/benchmarks`, not intuition.
- **Test every module.** Data structures, algorithms, and ranking logic all have unit tests independent of the API layer that uses them.

## License

MIT.
