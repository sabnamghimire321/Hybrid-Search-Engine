import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.core.preprocessing.pipeline import Pipeline
from search_engine.performance.parallel_indexer import build_index_parallel

def main():
    print(f"CPU cores available: {os.cpu_count()}")

    vocab = [f"word{i}" for i in range(200)]
    rng = random.Random(42)
    raw_docs = {i: " ".join(rng.choice(vocab) for _ in range(50)) for i in range(5000)}

    start = time.perf_counter()
    pipeline = Pipeline()
    seq_index = InvertedIndex()
    for doc_id, text in raw_docs.items():
        seq_index.add_document(doc_id, pipeline.process(text))
    seq_time = time.perf_counter() - start

    start = time.perf_counter()
    par_index = build_index_parallel(raw_docs, num_workers=4)
    par_time = time.perf_counter() - start

    print(f"Sequential: {seq_time:.3f}s")
    print(f"Parallel (4 workers): {par_time:.3f}s")
    print(f"Speedup: {seq_time / par_time:.2f}x")

if __name__ == "__main__":
    main()