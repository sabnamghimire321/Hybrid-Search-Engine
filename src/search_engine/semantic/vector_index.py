import math

from search_engine.datastructures.heap import Heap

def cosine_similarity_dense(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return dot / (mag_a * mag_b)

class VectorIndex:
    def __init__(self) -> None:
        self._vectors: dict[int, list[float]] = {}

    def add(self, doc_id: int, vector: list[float]) -> None:
        self._vectors[doc_id] = vector

    def remove(self, doc_id: int) -> bool:
        if doc_id in self._vectors:
            del self._vectors[doc_id]
            return True
        return False

    def get(self, doc_id: int) -> list[float] | None:
        return self._vectors.get(doc_id)

    def all_doc_ids(self) -> list[int]:
        return list(self._vectors.keys())

    def search(self, query_vector: list[float], top_k: int = 10) -> list[tuple[int, float]]:
        if not self._vectors:
            return []

        if top_k >= len(self._vectors):
            scored = [
                (cosine_similarity_dense(query_vector, vector), doc_id)
                for doc_id, vector in self._vectors.items()
            ]
            scored.sort(reverse=True)
            return [(doc_id, sim) for sim, doc_id in scored]

        heap = Heap(min_heap=True)
        for doc_id, vector in self._vectors.items():
            sim = cosine_similarity_dense(query_vector, vector)
            if len(heap) < top_k:
                heap.push((sim, doc_id))
            elif sim > heap.peek()[0]:
                heap.pop()
                heap.push((sim, doc_id))

        results = []
        while not heap.is_empty():
            results.append(heap.pop())
        results.reverse()

        return [(doc_id, sim) for sim, doc_id in results]

    def __len__(self) -> int:
        return len(self._vectors)

    def __contains__(self, doc_id: int) -> bool:
        return doc_id in self._vectors