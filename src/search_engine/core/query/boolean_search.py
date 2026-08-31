from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.core.preprocessing.pipeline import Pipeline


class BooleanSearch:
    def __init__(self, index: InvertedIndex, pipeline: Pipeline | None = None) -> None:
        self._index = index
        self._pipeline = pipeline or Pipeline()

    def _normalize(self, term: str) -> str:
        """Runs a single query word through the same preprocessing used
        at index time, so query terms and indexed terms are comparable."""
        processed = self._pipeline.process(term)
        return processed[0] if processed else term.lower()

    def search_and(self, terms: list[str]) -> set[int]:
        if not terms:
            return set()
        result: set[int] | None = None
        for term in terms:
            doc_ids = self._index.get_document_ids(self._normalize(term))
            result = doc_ids if result is None else result & doc_ids
            if not result:
                break  
        return result or set()

    def search_or(self, terms: list[str]) -> set[int]:
        result: set[int] = set()
        for term in terms:
            result |= self._index.get_document_ids(self._normalize(term))
        return result

    def search_not(self, term: str) -> set[int]:
        excluded = self._index.get_document_ids(self._normalize(term))
        return self._index.all_document_ids() - excluded

    def evaluate(self, query_terms: list[tuple[str, str]]) -> set[int]:
        """Evaluates a sequence of (operator, term) pairs left to right.

        The first entry's operator is ignored — it seeds the starting set.
        Example: [("OR", "python"), ("AND", "search"), ("NOT", "java")]
        means: (docs with "python") AND (docs with "search"), excluding
        any doc that contains "java".
        """
        if not query_terms:
            return set()

        _, first_term = query_terms[0]
        result = self._index.get_document_ids(self._normalize(first_term))

        for op, term in query_terms[1:]:
            doc_ids = self._index.get_document_ids(self._normalize(term))
            if op == "AND":
                result &= doc_ids
            elif op == "OR":
                result |= doc_ids
            elif op == "NOT":
                result -= doc_ids
            else:
                raise ValueError(f"Unknown boolean operator: {op!r}")

        return result