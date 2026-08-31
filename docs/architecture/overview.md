# Architecture Overview

This document walks through how a document gets indexed and how a query gets answered, module by module. For measured performance numbers rather than design rationale, see `docs/benchmarks`.

## Ingestion path

**Loaders** (`core/loaders`) turn a file on disk into plain text. Each source type — `.txt`, `.pdf`, `.html`, `.md` — has its own loader implementing a shared `extract_text` interface, so adding a new format means writing one small class, not touching the rest of the pipeline. The PDF loader raises explicitly when a file has no extractable text, since that usually means it's a scanned image that would need OCR rather than a bug in the loader.

**Preprocessing** (`core/preprocessing`) takes raw text through tokenization, stopword removal, and stemming. The pipeline is a fixed sequence of steps applied to every document and every query, which matters: if a query isn't preprocessed the same way as the documents it's searched against, matches get missed silently.

**Indexing** (`core/index`) builds an inverted index — a mapping from term to the list of documents (and positions, for phrase search) containing it. This is the data structure that makes search fast: instead of scanning every document for a term, you look the term up once and get back exactly the documents that contain it.

## Query path

**Query parsing** (`core/query`) supports `AND` / `OR` / `NOT` between bare terms and exact `"quoted phrases"`. Boolean queries resolve to postings-list intersections/unions against the inverted index; phrase queries additionally check that term positions are consecutive.

**Ranking** (`ranking`) turns a candidate document set into an ordered list. TF-IDF and BM25 are both implemented, with BM25 used by default — it improves on raw TF-IDF by saturating term-frequency scoring (a term appearing 100 times isn't 100x more relevant than it appearing once) and normalizing for document length. Cosine similarity and PageRank are also available. `ranking/evaluation.py` implements standard IR metrics (precision, recall, MAP) for comparing rankers against a labeled dataset.

**Semantic search** (`semantic`) adds an embedding-based path alongside keyword search. `embeddings.py` defines an `EmbeddingProvider` protocol with a dependency-free hash-based implementation as the default, and an optional `sentence-transformers` provider for real learned embeddings when that package is installed. `vector_index.py` stores document vectors and ranks by cosine similarity. `hybrid_search.py` combines BM25 and semantic scores by min-max normalizing each and blending them with a configurable weight, so keyword precision and semantic recall both contribute to the final ranking.

**RAG** (`semantic/rag.py`) sits on top of hybrid search. `QueryRewriter` expands a query with synonyms before retrieval. Two answer generators are available: `ExtractiveAnswerGenerator`, which pulls the most relevant sentence out of retrieved snippets with no external dependency, and `LLMAnswerGenerator`, which calls the Claude API for a generated answer when the `anthropic` package and an `ANTHROPIC_API_KEY` are available. The LLM path fails loudly with a clear message if either is missing rather than silently falling back, so it's obvious which mode is actually running.

## Storage

**Persistence** (`storage`) serializes the inverted index to a custom binary format (`serialization.py`) rather than pickling it, so the on-disk layout is stable and inspectable. `persistent_index.py` handles loading and saving; `mmap_store.py` memory-maps the file for reads instead of loading it entirely into memory, which matters once the index is larger than comfortably fits in RAM. `incremental.py` supports adding new documents to an existing on-disk index without a full rebuild.

## Crawler

The crawler (`crawler`) is a breadth-first web crawler built for correctness over scale: `robots.py` parses and enforces `robots.txt`, `url_frontier.py` deduplicates and queues URLs, `scheduler.py` controls crawl order and rate, and `html_parser.py` extracts links and titles from fetched pages. It's fetcher-agnostic — tests run against a `MockFetcher` with fixture pages, so the crawling logic is verified without making real network calls.

## Performance

**Performance tooling** (`performance`) includes a profiler for identifying hot paths, a parallel indexer that uses multiprocessing for CPU-bound preprocessing, an async search path for I/O-bound concurrent queries, and a benchmarking harness. The choice of multiprocessing vs. threading vs. asyncio here isn't arbitrary — see `docs/benchmarks/phase5_baseline.md` for the measurements that justify it.

## API and observability

The **API** (`api`) is a FastAPI app exposing search, suggest, indexing, and analytics endpoints. Auth is a simple API-key header check (`auth.py`); rate limiting is a fixed-window counter per client (`rate_limiter.py`); `analytics.py` persists query history to SQLite for the `/history` and `/analytics` endpoints. **Observability** (`observability`) adds request logging middleware and structured log configuration, so every request is traceable without needing an external APM tool.

## Data structures and algorithms

Everything above runs on data structures implemented in `datastructures/` — trie (for autocomplete), heap and priority queue (for top-k ranking), hash table, LRU cache, and graph (for the crawler and PageRank) — and algorithms in `algorithms/`: binary search, sorting, graph traversal (BFS/DFS), edit distance, and string matching. These aren't used because Python's built-ins are inadequate; they're implemented because understanding their complexity and trade-offs first-hand is a large part of the point of this project.
