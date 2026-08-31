from typing import Any


class Heap:
    def __init__(self, min_heap: bool = True) -> None:
        self._data: list[Any] = []
        self._min_heap = min_heap

    def _better(self, a: Any, b: Any) -> bool:
        return a < b if self._min_heap else a > b

    def push(self, item: Any) -> None:
        self._data.append(item)
        self._sift_up(len(self._data) - 1)

    def pop(self) -> Any:
        if not self._data:
            raise IndexError("pop from an empty heap")

        top = self._data[0]
        last = self._data.pop()
        if self._data:
            self._data[0] = last
            self._sift_down(0)
        return top

    def peek(self) -> Any:
        if not self._data:
            raise IndexError("peek from an empty heap")
        return self._data[0]

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent = (index - 1) // 2
            if self._better(self._data[index], self._data[parent]):
                self._data[index], self._data[parent] = self._data[parent], self._data[index]
                index = parent
            else:
                break

    def _sift_down(self, index: int) -> None:
        size = len(self._data)
        while True:
            left, right = 2 * index + 1, 2 * index + 2
            best = index

            if left < size and self._better(self._data[left], self._data[best]):
                best = left
            if right < size and self._better(self._data[right], self._data[best]):
                best = right

            if best == index:
                break
            self._data[index], self._data[best] = self._data[best], self._data[index]
            index = best

    @classmethod
    def heapify(cls, items: list, min_heap: bool = True) -> "Heap":
        heap = cls(min_heap=min_heap)
        heap._data = list(items)
        for i in reversed(range(len(heap._data) // 2)):
            heap._sift_down(i)
        return heap

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def __len__(self) -> int:
        return len(self._data)