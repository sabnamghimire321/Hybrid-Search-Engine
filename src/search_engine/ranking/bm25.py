import math

from search_engine.core.index.inverted_index import InvertedIndex

class BM25Ranker:
    def __init__(self, index: InvertedIndex, k1: float = 1.5, b: float = 0.75) -> None:
        self._index = index
        self._k1 = k1
        self._b = b
        self._avg_doc_length = self._compute_avg_doc_length()

    def _compute_avg_doc_length(self) -> float:
        doc_ids = self._index.all_document_ids()
        if not doc_ids:
            return 0.0
        total_length = sum(self._index.document_length(d) for d in doc_ids)
        return total_length / len(doc_ids)

    def idf(self, term: str) -> float:
        n = self._index.document_count
        df = self._index.document_frequency(term)
        return math.log(((n - df + 0.5) / (df + 0.5)) + 1)

    def _term_score(self, term: str, doc_id: int, length_norm: float) -> float:
        tf = self._index.term_frequency(term, doc_id)
        if tf == 0:
            return 0.0

        numerator = tf * (self._k1 + 1)
        denominator = tf + self._k1 * length_norm
        return self.idf(term) * (numerator / denominator)

    def score(self, query_terms: list[str], doc_id: int) -> float:
        if self._avg_doc_length == 0:
            return 0.0

        doc_length = self._index.document_length(doc_id)
        length_norm = 1 - self._b + self._b * (doc_length / self._avg_doc_length)

        return sum(self._term_score(term, doc_id, length_norm) for term in query_terms)

    def score_breakdown(self, query_terms: list[str], doc_id: int) -> dict[str, float]:
        if self._avg_doc_length == 0:
            return {term: 0.0 for term in query_terms}

        doc_length = self._index.document_length(doc_id)
        length_norm = 1 - self._b + self._b * (doc_length / self._avg_doc_length)

        return {term: self._term_score(term, doc_id, length_norm) for term in query_terms}