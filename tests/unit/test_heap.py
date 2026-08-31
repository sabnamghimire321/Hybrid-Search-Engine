import random
import pytest

from search_engine.datastructures.heap import Heap

def test_min_heap_pops_in_ascending_order():
    heap = Heap(min_heap=True)
    for x in [5, 3, 8, 1, 9, 2]:
        heap.push(x)

    popped = []
    while not heap.is_empty():
        popped.append(heap.pop())
    assert popped == [1, 2, 3, 5, 8, 9]


def test_max_heap_pops_in_descending_order():
    heap = Heap(min_heap=False)
    for x in [5, 3, 8, 1, 9, 2]:
        heap.push(x)

    popped = []
    while not heap.is_empty():
        popped.append(heap.pop())
    assert popped == [9, 8, 5, 3, 2, 1]


def test_peek_does_not_remove():
    heap = Heap(min_heap=True)
    heap.push(5)
    heap.push(1)
    assert heap.peek() == 1
    assert len(heap) == 2


def test_pop_empty_raises():
    heap = Heap()
    with pytest.raises(IndexError):
        heap.pop()


def test_peek_empty_raises():
    heap = Heap()
    with pytest.raises(IndexError):
        heap.peek()


def test_handles_duplicate_values():
    heap = Heap(min_heap=True)
    for x in [3, 1, 3, 1, 2]:
        heap.push(x)
    popped = [heap.pop() for _ in range(5)]
    assert popped == [1, 1, 2, 3, 3]


def test_heapify_builds_valid_heap():
    values = [7, 2, 9, 1, 5, 3, 8, 4, 6, 0]
    heap = Heap.heapify(values, min_heap=True)

    popped = []
    while not heap.is_empty():
        popped.append(heap.pop())
    assert popped == sorted(values)


def test_heapify_max_variant():
    values = [7, 2, 9, 1, 5]
    heap = Heap.heapify(values, min_heap=False)

    popped = []
    while not heap.is_empty():
        popped.append(heap.pop())
    assert popped == sorted(values, reverse=True)


def test_large_random_input_stays_correctly_ordered():
    random.seed(42)
    values = [random.randint(-1000, 1000) for _ in range(500)]

    heap = Heap(min_heap=True)
    for v in values:
        heap.push(v)

    popped = []
    while not heap.is_empty():
        popped.append(heap.pop())

    assert popped == sorted(values)