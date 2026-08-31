from collections import defaultdict

class InvertedIndex:
    def __init__(self) -> None:
        self._index: dict[str, dict[int, list[int]]] = defaultdict(dict)
        self._doc_lengths: dict[int, int] = {}
        self._document_terms: dict[int, set[str]] = {}
        self._document_count = 0

    def add_document(self, doc_id: int, tokens: list[str]) -> None:
        if doc_id in self._doc_lengths:
            raise ValueError(f"doc_id {doc_id} already indexed — re-indexing not supported yet")

        self._doc_lengths[doc_id] = len(tokens)
        self._document_terms[doc_id] = set(tokens)
        self._document_count += 1

        for position, term in enumerate(tokens):
            postings = self._index[term]
            postings.setdefault(doc_id, []).append(position)

    def remove_document(self, doc_id: int) -> bool:
        if doc_id not in self._doc_lengths:
            return False

        terms_in_doc = self._document_terms[doc_id]
        for term in terms_in_doc:
            postings = self._index.get(term)
            if postings and doc_id in postings:
                del postings[doc_id]
                if not postings:
                    del self._index[term]

        del self._doc_lengths[doc_id]
        del self._document_terms[doc_id]
        self._document_count -= 1
        return True

    def update_document(self, doc_id: int, tokens: list[str]) -> None:
        self.remove_document(doc_id)
        self.add_document(doc_id, tokens)

    def bulk_load(
        self,
        postings_by_term: dict[str, dict[int, list[int]]],
        doc_token_counts: dict[int, int],
    ) -> None:
        self._index = defaultdict(dict, postings_by_term)
        self._doc_lengths = dict(doc_token_counts)
        self._document_terms = {}
        for term, docs in postings_by_term.items():
            for doc_id in docs:
                self._document_terms.setdefault(doc_id, set()).add(term)
        self._document_count = len(self._doc_lengths)

    def document_terms(self, doc_id: int) -> set[str]:
        return self._document_terms.get(doc_id, set())

    def get_postings(self, term: str) -> dict[int, list[int]]:
        return self._index.get(term, {})

    def get_document_ids(self, term: str) -> set[int]:
        return set(self._index.get(term, {}).keys())

    def document_frequency(self, term: str) -> int:
        return len(self._index.get(term, {}))

    def term_frequency(self, term: str, doc_id: int) -> int:
        return len(self._index.get(term, {}).get(doc_id, []))

    def document_length(self, doc_id: int) -> int:
        return self._doc_lengths.get(doc_id, 0)

    @property
    def vocabulary_size(self) -> int:
        return len(self._index)

    @property
    def document_count(self) -> int:
        return self._document_count

    def all_terms(self) -> list[str]:
        return list(self._index.keys())

    def all_document_ids(self) -> set[int]:
        return set(self._doc_lengths.keys())