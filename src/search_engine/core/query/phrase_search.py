from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.core.preprocessing.pipeline import Pipeline


class PhraseSearch:
    def __init__(self, index: InvertedIndex, pipeline: Pipeline | None = None) -> None:
        self._index = index
        self._pipeline = pipeline or Pipeline()

    def search(self, phrase: str) -> set[int]:
        """Returns doc_ids where the phrase's terms appear in exact,
        consecutive order (after preprocessing both phrase and index)."""
        terms = self._pipeline.process(phrase)
        if not terms:
            return set()
        if len(terms) == 1:
            return self._index.get_document_ids(terms[0])

        postings_list = [self._index.get_postings(t) for t in terms]

        candidate_docs = set(postings_list[0].keys())
        for postings in postings_list[1:]:
            candidate_docs &= set(postings.keys())
            if not candidate_docs:
                return set()  
            
        matches: set[int] = set()
        for doc_id in candidate_docs:
            first_term_positions = postings_list[0][doc_id]
            later_position_sets = [set(postings[doc_id]) for postings in postings_list[1:]]

            for start in first_term_positions:
                if all(
                    (start + offset) in later_position_sets[offset - 1]
                    for offset in range(1, len(terms))
                ):
                    matches.add(doc_id)
                    break 
        return matches