import math

from search_engine.core.index.inverted_index import InvertedIndex

class TfIdfVectorizer:
    def __init__(self, index: InvertedIndex) -> None:
        self._index = index

    def idf(self, term: str) -> float:
        df = self._index.document_frequency(term)
        if df == 0:
            return 0.0
        return math.log10(self._index.document_count / df)

    def tf(self, term: str, doc_id: int) -> float:
        count = self._index.term_frequency(term, doc_id)
        if count == 0:
            return 0.0
        return 1.0 + math.log10(count)

    def tf_idf(self, term: str, doc_id: int) -> float:
        return self.tf(term, doc_id) * self.idf(term)

    def vectorize_document(self, doc_id: int) -> dict[str, float]:
        terms = self._index.document_terms(doc_id)
        return {term: self.tf_idf(term, doc_id) for term in terms}

    def vectorize_query(self, query_terms: list[str]) -> dict[str, float]:
        term_counts: dict[str, int] = {}
        for term in query_terms:
            term_counts[term] = term_counts.get(term, 0) + 1

        vector = {}
        for term, count in term_counts.items():
            tf = 1.0 + math.log10(count) if count > 0 else 0.0
            vector[term] = tf * self.idf(term)
        return vector

    def score(self, query_terms: list[str], doc_id: int) -> float:
        return sum(self.tf_idf(term, doc_id) for term in query_terms)