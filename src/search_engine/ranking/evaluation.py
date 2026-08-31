import math

def precision_at_k(retrieved: list, relevant: set, k: int) -> float:
    """Fraction of the top-k retrieved documents that are relevant."""
    top_k = retrieved[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for doc_id in top_k if doc_id in relevant)
    return hits / len(top_k)

def recall_at_k(retrieved: list, relevant: set, k: int) -> float:
    if not relevant:
        return 0.0
    top_k = retrieved[:k]
    hits = sum(1 for doc_id in top_k if doc_id in relevant)
    return hits / len(relevant)

def _dcg_at_k(ordered_relevances: list[float], k: int) -> float:
    """DCG for a list of relevance grades already in RANKED order."""
    return sum(
        (2**relevance - 1) / math.log2(i + 2)
        for i, relevance in enumerate(ordered_relevances[:k])
    )

def ndcg_at_k(retrieved: list, relevance_scores: dict, k: int) -> float:
    actual_relevances = [relevance_scores.get(doc_id, 0) for doc_id in retrieved]
    dcg = _dcg_at_k(actual_relevances, k)

    ideal_relevances = sorted(relevance_scores.values(), reverse=True)
    idcg = _dcg_at_k(ideal_relevances, k)

    if idcg == 0:
        return 0.0

    return dcg / idcg