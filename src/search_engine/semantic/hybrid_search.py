from search_engine.ranking.bm25 import BM25Ranker
from search_engine.semantic.embeddings import EmbeddingProvider
from search_engine.semantic.vector_index import cosine_similarity_dense

def _min_max_normalize(scores: dict[int, float]) -> dict[int, float]:
    if not scores:
        return {}

    values = list(scores.values())
    lo, hi = min(values), max(values)

    if hi == lo:
        return {doc_id: 0.5 for doc_id in scores}

    return {doc_id: (score - lo) / (hi - lo) for doc_id, score in scores.items()}

class HybridSearch:
    def __init__(
        self,
        bm25_ranker: BM25Ranker,
        embedding_provider: EmbeddingProvider,
        doc_vectors: dict[int, list[float]],
        keyword_weight: float = 0.5,
    ) -> None:

        self._bm25 = bm25_ranker
        self._embedding_provider = embedding_provider
        self._doc_vectors = doc_vectors
        self._keyword_weight = keyword_weight

    def search(
        self, query: str, query_terms: list[str], candidate_doc_ids: list[int], top_k: int = 10
    ) -> list[tuple[int, float]]:
        if not candidate_doc_ids:
            return []

        keyword_scores = {
            doc_id: self._bm25.score(query_terms, doc_id) for doc_id in candidate_doc_ids
        }

        query_vector = self._embedding_provider.embed(query)
        semantic_scores = {
            doc_id: cosine_similarity_dense(query_vector, self._doc_vectors.get(doc_id, []))
            for doc_id in candidate_doc_ids
        }

        normalized_keyword = _min_max_normalize(keyword_scores)
        normalized_semantic = _min_max_normalize(semantic_scores)

        combined = {
            doc_id: (
                self._keyword_weight * normalized_keyword.get(doc_id, 0.0)
                + (1 - self._keyword_weight) * normalized_semantic.get(doc_id, 0.0)
            )
            for doc_id in candidate_doc_ids
        }

        ranked = sorted(combined.items(), key=lambda pair: pair[1], reverse=True)
        return ranked[:top_k]