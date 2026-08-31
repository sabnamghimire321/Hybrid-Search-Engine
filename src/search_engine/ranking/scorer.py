from typing import Any
from search_engine.datastructures.heap import Heap

class ResultScorer:
    def __init__(
        self,
        ranker: Any,
        pagerank_scores: dict[int, float] | None = None,
        pagerank_weight: float = 0.0,
    ) -> None:
        self._ranker = ranker
        self._pagerank_scores = pagerank_scores or {}
        self._pagerank_weight = pagerank_weight

    def score_document(self, query_terms: list[str], doc_id: int) -> float:
        relevance = self._ranker.score(query_terms, doc_id)
        authority = self._pagerank_scores.get(doc_id, 0.0)
        return relevance + self._pagerank_weight * authority

    def rank(
        self,
        query_terms: list[str],
        candidate_doc_ids: list[int] | set[int],
        top_k: int | None = None,
    ) -> list[tuple[int, float]]:
        scored = [
            (self.score_document(query_terms, doc_id), doc_id) for doc_id in candidate_doc_ids
        ]

        if top_k is None or top_k >= len(scored):
            scored.sort(reverse=True)
            return [(doc_id, score) for score, doc_id in scored]

        heap = Heap(min_heap=True)
        for score, doc_id in scored:
            if len(heap) < top_k:
                heap.push((score, doc_id))
            elif score > heap.peek()[0]:
                heap.pop()
                heap.push((score, doc_id))

        results = []
        while not heap.is_empty():
            results.append(heap.pop())
        results.reverse()

        return [(doc_id, score) for score, doc_id in results]