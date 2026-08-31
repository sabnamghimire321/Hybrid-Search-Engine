import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.core.preprocessing.pipeline import Pipeline
from search_engine.ranking.bm25 import BM25Ranker
from search_engine.ranking.evaluation import ndcg_at_k, precision_at_k, recall_at_k
from search_engine.ranking.scorer import ResultScorer
from search_engine.ranking.tfidf import TfIdfVectorizer
from search_engine.semantic.embeddings import HashEmbeddingProvider
from search_engine.semantic.hybrid_search import HybridSearch

from relevance_dataset import DOCUMENTS, RELEVANCE_JUDGMENTS, relevant_doc_ids

K = 5


def build_index() -> tuple[InvertedIndex, Pipeline]:
    pipeline = Pipeline()
    index = InvertedIndex()
    for doc_id, text in DOCUMENTS.items():
        index.add_document(doc_id, pipeline.process(text))
    return index, pipeline


def evaluate_ranking(ranked_doc_ids: list[int], query: str) -> dict:
    relevant = relevant_doc_ids(query)
    relevance_scores = RELEVANCE_JUDGMENTS[query]
    return {
        "precision@5": precision_at_k(ranked_doc_ids, relevant, K),
        "recall@5": recall_at_k(ranked_doc_ids, relevant, K),
        "ndcg@5": ndcg_at_k(ranked_doc_ids, relevance_scores, K),
    }

def main():
    index, pipeline = build_index()

    tfidf = TfIdfVectorizer(index)
    bm25 = BM25Ranker(index)
    embedding_provider = HashEmbeddingProvider(dimension=64)
    doc_vectors = {
        doc_id: embedding_provider.embed(text) for doc_id, text in DOCUMENTS.items()
    }
    hybrid = HybridSearch(bm25, embedding_provider, doc_vectors, keyword_weight=0.7)

    all_doc_ids = list(DOCUMENTS.keys())

    results_by_method = {"TF-IDF": [], "BM25": [], "Hybrid": []}

    for query in RELEVANCE_JUDGMENTS:
        query_terms = pipeline.process(query)

        tfidf_ranked = sorted(
            all_doc_ids, key=lambda d: tfidf.score(query_terms, d), reverse=True
        )
        tfidf_metrics = evaluate_ranking(tfidf_ranked, query)
        results_by_method["TF-IDF"].append(tfidf_metrics)

        bm25_scorer = ResultScorer(bm25)
        bm25_ranked = [doc_id for doc_id, _ in bm25_scorer.rank(query_terms, all_doc_ids, top_k=K)]
        bm25_metrics = evaluate_ranking(bm25_ranked, query)
        results_by_method["BM25"].append(bm25_metrics)

        hybrid_ranked = [
            doc_id for doc_id, _ in hybrid.search(query, query_terms, all_doc_ids, top_k=K)
        ]
        hybrid_metrics = evaluate_ranking(hybrid_ranked, query)
        results_by_method["Hybrid"].append(hybrid_metrics)

        print(f"\nQuery: {query!r}")
        print(f"  TF-IDF top-{K}: {tfidf_ranked[:K]}  {tfidf_metrics}")
        print(f"  BM25   top-{K}: {bm25_ranked}  {bm25_metrics}")
        print(f"  Hybrid top-{K}: {hybrid_ranked}  {hybrid_metrics}")

    print("\n" + "=" * 60)
    print(f"AVERAGE METRICS ACROSS ALL {len(RELEVANCE_JUDGMENTS)} QUERIES")
    print("=" * 60)
    print(f"{'Method':<10} {'Precision@5':>12} {'Recall@5':>10} {'NDCG@5':>8}")
    for method, per_query_results in results_by_method.items():
        avg_precision = sum(r["precision@5"] for r in per_query_results) / len(per_query_results)
        avg_recall = sum(r["recall@5"] for r in per_query_results) / len(per_query_results)
        avg_ndcg = sum(r["ndcg@5"] for r in per_query_results) / len(per_query_results)
        print(f"{method:<10} {avg_precision:>12.3f} {avg_recall:>10.3f} {avg_ndcg:>8.3f}")


if __name__ == "__main__":
    main()