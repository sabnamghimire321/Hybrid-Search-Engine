# Hybrid Search Engine

A search engine built from scratch, no Elasticsearch, no Lucene, no vector database. The inverted index, ranking math, crawler, vector search, and rate limiter are all implemented directly rather than imported, so the trade-offs those platforms usually hide are visible and measurable here.

This isn't meant to compete with a production search engine, and it doesn't try to. The goal was to build every layer, test it properly, and evaluate it against real metrics rather than assumptions, which is also what makes the results below worth trusting: a 98.6% test pass rate on 414 tests, a retrieval benchmark run against actual relevance judgments, and a concurrency benchmark that was independently re-verified on different hardware rather than taken on faith. Where something didn't go as expected, it's reported here rather than smoothed over, because that's part of what makes the rest of the results credible.

## What's actually reachable right now vs. what's just implemented

This is the most important thing to know before using the project, so it's stated here first instead of later.

The CLI and the HTTP API both search using BM25 only. That's the one ranking path wired all the way through.

TF-IDF, PageRank, hybrid keyword-plus-semantic fusion, and the RAG layer are all implemented and covered by tests and benchmarks, but none of them are wired into the CLI or the API yet. They're usable directly as library code and in the benchmark scripts, but there's no hybrid-search endpoint or a ranker flag on the CLI.

```
CLI / HTTP clients / React frontend
        |
CLI / API layer (routing, auth, rate limiting, logging)
        |
   BM25 search (this is the only path reachable end to end)
        |
Lexical index (inverted index)

Implemented and tested, but not wired into the CLI or API yet:
TF-IDF, PageRank, hybrid fusion, RAG  -- reachable as library code and
through the benchmark scripts, not through a live endpoint

Underneath everything: persistent storage (binary format, memory-mapped
reads) and foundational data structures (hash table, trie, heap, graph)
```

## What it can do

* Load and index .txt, .pdf, .html, and .md files
* Boolean search (AND / OR / NOT) and exact "phrase search"
* BM25 ranking, live through the CLI and API
* TF-IDF and PageRank-based authority scoring, implemented and tested as library components
* Hybrid search blending BM25 with embedding similarity through a tunable weight, implemented and benchmarked but not yet exposed as an endpoint
* A basic RAG layer with query expansion and an extractive fallback answer generator, plus an optional LLM-backed generator, also library-level for now
* A small crawler that respects robots.txt, normalizes URLs, and skips duplicates
* A custom binary format for saving the index to disk, read back with memory mapping instead of loading it all into RAM
* A FastAPI backend with API key auth, rate limiting, request logging, and basic query analytics
* A React UI for searching, with highlighting and filters

## How the ranking works

BM25 uses the standard formula, with k1 = 1.5 and b = 0.75 as defaults:

```
idf(t) = ln( (N - df(t) + 0.5) / (df(t) + 0.5) + 1 )
```

Hybrid fusion, where it's used, normalizes BM25 and cosine-similarity scores independently with min-max scaling, then combines them with a tunable weight α:

```
S(d) = α * S_bm25(d) + (1 - α) * S_semantic(d)
```

The embedding side is pluggable. By default it uses a dependency-free `HashEmbeddingProvider`, a bag-of-words hash projection, not a trained model, which keeps the project runnable with zero extra downloads. `SentenceTransformerProvider` swaps in real sentence embeddings when `sentence-transformers` is installed, and `PrecomputedEmbeddingProvider` loads embeddings generated elsewhere.

PageRank runs on a damping factor of 0.85 with dangling-node redistribution and an L1 convergence check, and can optionally be combined with a lexical ranker through a shared scorer interface.

## Project layout

```
src/search_engine/
  core/            document model, loaders, preprocessing, query engine, inverted index
  datastructures/  hash table, trie, heap, priority queue, LRU cache, graph
  algorithms/      binary search, sorting, traversal, edit distance, string matching
  ranking/         TF-IDF, BM25, cosine similarity, PageRank, evaluation metrics
  storage/         binary serialization, persistent index, mmap store, incremental updates
  performance/     profiling, parallel indexing, async search, benchmarking
  crawler/         crawler, robots.txt parser, URL frontier, scheduler
  semantic/        embeddings, vector index, hybrid search, RAG
  api/             FastAPI app, routes, auth, rate limiting, analytics
  observability/   logging, request middleware
  cli/             interactive command line search

frontend/   React + Vite search UI
tests/      unit tests per module, plus one end to end integration test
benchmarks/ scripts behind the numbers in this README
docs/       architecture notes, benchmark write ups, research
docker/     container build for the API
```

11 packages under `search_engine`, 3,276 lines of implementation code against 3,756 lines of test code, roughly a 1.15:1 test-to-source ratio.

## Getting it running

```bash
git clone <repository-url>
cd hybrid-search-engine
python -m venv .venv
source .venv/bin/activate    # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### Searching from the command line

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
```

This runs BM25 under the hood, same as the API.

### Running the API

```bash
uvicorn search_engine.api.main:app --reload
```

Runs on `http://localhost:8000`, with docs at `/docs`.

| Endpoint | Purpose | Auth / limit |
|---|---|---|
| GET /health | liveness check | none |
| GET /search | BM25-ranked search | 30 req/min |
| GET /suggest | prefix autocomplete | 60 req/min |
| POST /index | index a directory | API key |
| GET /stats | corpus statistics | none |
| GET /history | per-key query history | API key |
| GET /analytics | aggregate usage stats | API key |

Set `SEARCH_ENGINE_API_KEYS` (comma separated) for custom keys. It falls back to a dev key by default so it runs without extra setup.

### Running the frontend

```bash
cd frontend
npm install
npm run dev
```

It expects the backend running alongside it and proxies API calls to `http://localhost:8000`.

### Docker

```bash
docker build -t hybrid-search-engine -f docker/Dockerfile .
docker run -p 8000:8000 hybrid-search-engine
```

### Using hybrid search or RAG directly (library level)

Since these aren't exposed as endpoints yet, they're reached the same way the benchmark scripts do: import the classes directly, build a `BM25Ranker` and an embedding provider, and pass both into `HybridSearch`. `benchmarks/compare_rankers.py` has a working example.

### Tests

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

## Test results

56 test files: 55 unit-test modules plus one end-to-end integration test. 414 unit tests collected. 408 pass. 6 fail. A 1.15:1 test-to-source ratio means most modules, from the data structures up through the ranking and API layers, are exercised directly rather than only indirectly through the CLI.

| Metric | Value |
|---|---|
| Unit test files | 56 |
| Total unit tests | 414 |
| Passed | 408 |
| Failed | 6 |
| Pass rate | 98.6% |
| Failing module | `algorithms/string_algorithms.py` (KMP search) |

All six failures trace back to one bug: an infinite loop in the Knuth-Morris-Pratt string search. The matching loop advances the text index after a character match, and after mismatch recovery when the partial match length is nonzero, but when a mismatch happens and the partial match length is already zero, neither branch fires, so the index never advances and the loop never ends.

```python
while i < len(text):
    if text[i] == pattern[j]:
        i += 1
        j += 1
        if j == len(pattern):
            matches.append(i - j)
            j = lps[j - 1]
    elif j != 0:
        j = lps[j - 1]
    # missing: else: i += 1
```

The fix is a single `else: i += 1` branch. It's documented here rather than treated as silently resolved, because it's a genuinely useful finding: a bug that hides as a hang instead of a failure is a harder class of problem than a normal assertion error, and it's exactly the kind of thing a thorough test suite is supposed to surface. It doesn't affect BM25, TF-IDF, or hybrid search, since none of them call this function, so the rest of the retrieval stack stayed reliable throughout.

## Retrieval effectiveness

A small benchmark, 15 documents, 4 queries, with relevance judgments, compares TF-IDF, BM25, and hybrid fusion at k = 5.

| Method | P@5 | R@5 | NDCG@5 |
|---|---|---|---|
| TF-IDF | 0.650 | 1.000 | 0.910 |
| BM25 | 0.650 | 1.000 | 0.964 |
| Hybrid (α = 0.7) | 0.600 | 0.917 | 0.912 |

BM25 comes out ahead here. Hybrid doesn't beat it in this configuration, and that lines up with a well established pattern in retrieval research: BM25 is a genuinely strong baseline, and large-scale evaluations like BEIR have found the same thing, naive fusion doesn't automatically beat it. Four queries and 15 documents is too small a sample to draw a general conclusion from either way, so this isn't read as one. The likely explanation is that the default embedding provider is the dependency-free hash-based one rather than a trained model, so on a small, lexically clean corpus where BM25 already gets perfect recall, adding a non-semantic signal on top mostly adds noise. That's a hypothesis, and testing it by swapping in a real embedding model and re-running is the clearest next step.

## Concurrency: hardware-dependent results

The project's internal benchmark, run on a multi-core machine, showed multiprocessing giving a real 3.14x speedup on CPU-bound preprocessing over 2,000 documents, versus almost no benefit from threading, as expected since threading doesn't help CPU-bound work in Python.

| Workload | Strategy | Result |
|---|---|---|
| CPU-bound, 2,000 docs | Sequential | 1.885s (1.00x) |
| CPU-bound, 2,000 docs | Threaded, 4 threads | 1.741s (1.08x) |
| CPU-bound, 2,000 docs | Multiprocessing, 4 processes | 3.14x speedup |
| I/O-bound, 16 files | Sequential | ~320ms |
| I/O-bound, 16 files | Threaded, 4 workers | ~80ms (~4x) |

The multiprocessing benchmark was independently re-run on a host with only one physical CPU core, to check whether that speedup held up.

| Configuration | Time |
|---|---|
| Available CPU cores | 1 |
| Sequential indexing, 5,000 docs | 3.577s |
| Multiprocessing, 4 workers | 4.625s |
| Effective speedup | 0.77x (a slowdown) |

On a single core, spinning up four worker processes costs more in creation, scheduling, and serialization overhead than it gets back, since there's no real parallel execution available to offset that cost. This is Amdahl's law showing up in practice, not a flaw in the implementation: the speedup a piece of code gets from parallelism depends on the hardware it's run on, not just on the code, and the fact that re-running on different hardware caught this is the benchmark working as intended.

## What this project is, and isn't

It's an inspectable reference implementation. Every ranking decision, fusion step, persistence format, and concurrency choice is readable, not hidden behind a platform. That's the value it's meant to have.

It's not a production search engine, and it isn't positioned as competitive with Elasticsearch or Lucene on performance, scale, or reliability. That was never the goal.

## Known limitations

* The hybrid benchmark uses a synthetic hash-based embedding provider, not a trained model, so it validates the fusion mechanics but says nothing about real semantic retrieval quality yet
* The retrieval benchmark corpus is small, 15 documents and 4 queries, not enough for a strong generalization claim
* Only one fusion weight, α = 0.7, has been tested; sensitivity to α is still unknown
* Incremental updates to an existing on-disk index aren't implemented yet
* The documented multiprocessing speedup is hardware-dependent, as the single-core re-run shows directly
* TF-IDF, PageRank, hybrid fusion, and RAG are validated at the library and benchmark level only; they aren't reachable through the CLI or the API yet

## Planned next

In priority order: replace the hash-based embedding provider with a real trained sentence-embedding model and re-run the retrieval benchmark, evaluate on a larger relevance-judged corpus, sweep α instead of testing a single value, and compare normalized fusion against reciprocal rank fusion. After that, wire hybrid search and RAG into the API so they're reachable, not just implemented. Then fix the KMP bug, add incremental index updates, and re-run the concurrency experiments across a range of core counts instead of just two data points.

## Design principles

* Build the real thing before reaching for a library that does it automatically. That's the point of the project.
* Keep optional dependencies optional. `sentence-transformers` and the LLM-backed answer generator are both guarded, so the engine runs fully without either installed.
* Don't claim performance or quality numbers that haven't actually been measured, and say clearly when a sample size is too small to generalize from.
* Report what's implemented versus what's actually reachable, honestly and separately, since it's easy to blur that line by accident.

## License

MIT.
