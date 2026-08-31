import itertools
from typing import Any

from search_engine.datastructures.heap import Heap


class PriorityQueue:
    def __init__(self, min_first: bool = True) -> None:
        self._min_first = min_first
        self._heap = Heap(min_heap=min_first)
        self._counter = itertools.count()

    def push(self, item: Any, priority: float) -> None:
        count = next(self._counter)
        tiebreak = count if self._min_first else -count
        self._heap.push((priority, tiebreak, item))

    def pop(self) -> Any:
        _priority, _tiebreak, item = self._heap.pop()
        return item

    def pop_with_priority(self) -> tuple[Any, float]:
        priority, _tiebreak, item = self._heap.pop()
        return item, priority

    def peek(self) -> Any:
        _priority, _tiebreak, item = self._heap.peek()
        return item

    def is_empty(self) -> bool:
        return self._heap.is_empty()

    def __len__(self) -> int:
        return len(self._heap)