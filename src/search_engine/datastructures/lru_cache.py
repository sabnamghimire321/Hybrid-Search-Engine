from typing import Any

class _Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: Any = None, value: Any = None) -> None:
        self.key = key
        self.value = value
        self.prev: "_Node | None" = None
        self.next: "_Node | None" = None

class LRUCache:
    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self._capacity = capacity
        self._map: dict[Any, _Node] = {}
        self._head = _Node()
        self._tail = _Node()
        self._head.next = self._tail
        self._tail.prev = self._head

    def _remove(self, node: _Node) -> None:
        """Unlinks `node` from wherever it currently sits in the list."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_at_front(self, node: _Node) -> None:
        """Inserts `node` right after the head sentinel (most-recent slot)."""
        node.next = self._head.next
        node.prev = self._head
        self._head.next.prev = node
        self._head.next = node

    def get(self, key: Any) -> Any:
        if key not in self._map:
            raise KeyError(key)

        node = self._map[key]
        self._remove(node)
        self._insert_at_front(node)
        return node.value

    def get_or_default(self, key: Any, default: Any = None) -> Any:
        try:
            return self.get(key)
        except KeyError:
            return default

    def put(self, key: Any, value: Any) -> None:
        if key in self._map:
            node = self._map[key]
            node.value = value
            self._remove(node)
            self._insert_at_front(node)
            return

        if len(self._map) >= self._capacity:
            lru_node = self._tail.prev 
            self._remove(lru_node)
            del self._map[lru_node.key]

        new_node = _Node(key, value)
        self._map[key] = new_node
        self._insert_at_front(new_node)

    def __contains__(self, key: Any) -> bool:
        return key in self._map

    def __len__(self) -> int:
        return len(self._map)