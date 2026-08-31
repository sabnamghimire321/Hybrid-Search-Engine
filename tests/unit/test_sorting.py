import random

from search_engine.algorithms.sorting import merge_sort, quick_sort

def test_merge_sort_matches_builtin_sorted():
    random.seed(1)
    values = [random.randint(-100, 100) for _ in range(200)]
    assert merge_sort(values) == sorted(values)

def test_quick_sort_matches_builtin_sorted():
    random.seed(1)
    values = [random.randint(-100, 100) for _ in range(200)]
    assert quick_sort(values) == sorted(values)

def test_both_handle_empty_and_single_element():
    assert merge_sort([]) == []
    assert quick_sort([]) == []
    assert merge_sort([42]) == [42]
    assert quick_sort([42]) == [42]

def test_both_handle_duplicates():
    values = [3, 1, 3, 2, 1, 3, 2]
    assert merge_sort(values) == sorted(values)
    assert quick_sort(values) == sorted(values)

def test_quick_sort_on_already_sorted_input_does_not_blow_up():
    already_sorted = list(range(2000))
    assert quick_sort(already_sorted) == already_sorted

def test_quick_sort_on_reverse_sorted_input():
    reverse_sorted = list(range(2000, 0, -1))
    assert quick_sort(reverse_sorted) == sorted(reverse_sorted)

def test_merge_sort_is_stable():
    class Tagged:
        def __init__(self, value, tag):
            self.value = value
            self.tag = tag

        def __le__(self, other):
            return self.value <= other.value

    tagged_items = [Tagged(1, "a"), Tagged(2, "b"), Tagged(1, "c"), Tagged(2, "d"), Tagged(1, "e")]
    sorted_tagged = merge_sort(tagged_items)

    ones_in_order = [t.tag for t in sorted_tagged if t.value == 1]
    assert ones_in_order == ["a", "c", "e"]  

def test_original_list_is_not_mutated():
    original = [5, 3, 1, 4, 2]
    original_copy = original[:]
    merge_sort(original)
    quick_sort(original)
    assert original == original_copy