import multiprocessing
import os

from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.core.preprocessing.pipeline import Pipeline

PartialResult = tuple[dict[int, int], dict[str, dict[int, list[int]]]]

def _process_chunk(chunk: list[tuple[int, str]]) -> PartialResult:
    pipeline = Pipeline()
    doc_lengths: dict[int, int] = {}
    postings: dict[str, dict[int, list[int]]] = {}

    for doc_id, raw_text in chunk:
        tokens = pipeline.process(raw_text)
        doc_lengths[doc_id] = len(tokens)
        for position, term in enumerate(tokens):
            postings.setdefault(term, {}).setdefault(doc_id, []).append(position)

    return doc_lengths, postings

def _merge_partial_results(results: list[PartialResult]) -> InvertedIndex:
    merged_doc_lengths: dict[int, int] = {}
    merged_postings: dict[str, dict[int, list[int]]] = {}

    for doc_lengths, postings in results:
        merged_doc_lengths.update(doc_lengths)
        for term, doc_postings in postings.items():
            merged_postings.setdefault(term, {}).update(doc_postings)

    index = InvertedIndex()
    index.bulk_load(merged_postings, merged_doc_lengths)
    return index

def build_index_parallel(
    raw_documents: dict[int, str],
    num_workers: int | None = None,
    chunk_size: int | None = None,
) -> InvertedIndex:
    if num_workers is None:
        num_workers = min(os.cpu_count() or 2, 4)

    items = list(raw_documents.items())
    if not items:
        return InvertedIndex()

    if chunk_size is None:
        chunk_size = max(1, -(-len(items) // num_workers))

    chunks = [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]

    with multiprocessing.Pool(processes=num_workers) as pool:
        partial_results = pool.map(_process_chunk, chunks)

    return _merge_partial_results(partial_results)