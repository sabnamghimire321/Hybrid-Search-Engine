from pathlib import Path
from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.storage.serialization import deserialize_index, serialize_index

class PersistentIndexStore:
    def save(self, index: InvertedIndex, path: str) -> None:
        """Serializes the index and writes it to `path` in one shot."""
        data = serialize_index(index)
        Path(path).write_bytes(data)

    def load(self, path: str) -> InvertedIndex:
        resolved = Path(path)
        if not resolved.exists():
            raise FileNotFoundError(f"No such index file: {resolved}")

        data = resolved.read_bytes()
        return deserialize_index(data)

    def exists(self, path: str) -> bool:
        return Path(path).exists()