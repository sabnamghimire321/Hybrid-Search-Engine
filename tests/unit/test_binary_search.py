from search_engine.algorithms.binary_search import (
    binary_search,
    binary_search_leftmost,
    binary_search_rightmost,
)

def test_binary_search_finds_present_element():
    arr = [1, 3, 5, 7, 9, 11]
    assert binary_search(arr, 7) == 3

def test_binary_search_missing_element_returns_negative_one():
    arr = [1, 3, 5, 7, 9]
    assert binary_search(arr, 4) == -1

def test_binary_search_empty_array():
    assert binary_search([], 5) == -1

def test_binary_search_single_element():
    assert binary_search([5], 5) == 0
    assert binary_search([5], 3) == -1

def test_leftmost_finds_first_occurrence_of_duplicate():
    arr = [1, 2, 2, 2, 3, 4]
    assert binary_search_leftmost(arr, 2) == 1

def test_leftmost_insertion_point_for_missing_value():
    arr = [1, 3, 5, 7]
    assert binary_search_leftmost(arr, 4) == 2  

def test_rightmost_finds_position_past_last_occurrence():
    arr = [1, 2, 2, 2, 3, 4]
    assert binary_search_rightmost(arr, 2) == 4

def test_leftmost_and_rightmost_bracket_all_duplicates():
    arr = [1, 2, 2, 2, 3]
    left = binary_search_leftmost(arr, 2)
    right = binary_search_rightmost(arr, 2)
    assert arr[left:right] == [2, 2, 2]

def test_rightmost_insertion_point_beyond_all_elements():
    arr = [1, 2, 3]
    assert binary_search_rightmost(arr, 10) == 3
    assert binary_search_leftmost(arr, 10) == 3