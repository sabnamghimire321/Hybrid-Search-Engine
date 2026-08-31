from typing import Any, Iterator

class HashTable:
    _INITIAL_CAPACITY = 8
    _LOAD_FACTOR_THRESHOLD = 0.75

    def __init__(self) -> None:
        self._capacity = self._INITIAL_CAPACITY
        self._buckets: list[list[tuple[Any, Any]]] = [
            [] for _ in range(self._capacity)
        ]
        self._size = 0

    def _bucket_index(self, key: Any) -> int:
        return hash(key) % self._capacity

    def put(self, key: Any, value: Any) -> None:
        if (self._size + 1) / self._capacity >= self._LOAD_FACTOR_THRESHOLD:
            self._resize()

        bucket = self._buckets[self._bucket_index(key)]

        for i, (existing_key, _) in enumerate(bucket):
            if existing_key == key:
                bucket[i] = (key, value)
                return

        bucket.append((key, value))
        self._size += 1

    def get(self, key: Any) -> Any:
        bucket = self._buckets[self._bucket_index(key)]

        for existing_key, value in bucket:
            if existing_key == key:
                return value

        raise KeyError(key)

    def get_or_default(self, key: Any, default: Any = None) -> Any:
        try:
            return self.get(key)
        except KeyError:
            return default

    def contains(self, key: Any) -> bool:
        bucket = self._buckets[self._bucket_index(key)]
        return any(existing_key == key for existing_key, _ in bucket)

    def delete(self, key: Any) -> None:
        bucket = self._buckets[self._bucket_index(key)]

        for i, (existing_key, _) in enumerate(bucket):
            if existing_key == key:
                del bucket[i]
                self._size -= 1
                return

        raise KeyError(key)

    def _resize(self) -> None:
        old_buckets = self._buckets

        self._capacity *= 2

        self._buckets = [[] for _ in range(self._capacity)]

        self._size = 0

        for bucket in old_buckets:
            for key, value in bucket:
                self.put(key, value)

    def keys(self) -> Iterator[Any]:
        for bucket in self._buckets:
            for key, _ in bucket:
                yield key

    def values(self) -> Iterator[Any]:
        for bucket in self._buckets:
            for _, value in bucket:
                yield value

    def items(self) -> Iterator[tuple[Any, Any]]:
        for bucket in self._buckets:
            yield from bucket

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key: Any) -> bool:
        return self.contains(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        self.put(key, value)

    def __getitem__(self, key: Any) -> Any:
        return self.get(key)

    def __delitem__(self, key: Any) -> None:
        self.delete(key)

    def __iter__(self) -> Iterator[Any]:
        return self.keys()