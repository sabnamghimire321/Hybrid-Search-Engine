import hashlib
import json
from typing import Protocol

class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> list[float]: ...

    @property
    def dimension(self) -> int: ...

class HashEmbeddingProvider:
    def __init__(self, dimension: int = 64) -> None:
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self._dimension
        words = text.lower().split()
        if not words:
            return vector

        for word in words:
            bucket = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16) % self._dimension
            vector[bucket] += 1.0

        magnitude = sum(x * x for x in vector) ** 0.5
        if magnitude > 0:
            vector = [x / magnitude for x in vector]
        return vector


class SentenceTransformerProvider:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(model_name)
            self._dimension = self._model.get_sentence_embedding_dimension()
        except Exception as e:
            raise ImportError(
                "SentenceTransformerProvider could not be initialized (this can be "
                "a missing package, a broken install, missing system dependencies, "
                "or no network access to download model weights). This is "
                "intentionally NOT a required dependency of this project -- use "
                "HashEmbeddingProvider for testing/development, or generate real "
                "embeddings offline (e.g. in a free Google Colab notebook) and load "
                f"them with PrecomputedEmbeddingProvider instead. Original error: {e}"
            ) from e

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, text: str) -> list[float]:
        return self._model.encode(text).tolist()

class PrecomputedEmbeddingProvider:
    def __init__(self, embeddings: dict[str, list[float]]) -> None:
        if not embeddings:
            raise ValueError("embeddings dict cannot be empty")
        self._embeddings = embeddings
        self._dimension = len(next(iter(embeddings.values())))

    @classmethod
    def from_json_file(cls, path: str) -> "PrecomputedEmbeddingProvider":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(data)

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, key: str) -> list[float]:
        if key not in self._embeddings:
            raise KeyError(f"No precomputed embedding for key: {key!r}")
        return self._embeddings[key]