import random

from search_engine.algorithms.string_algorithms import kmp_search, rabin_karp_search

def test_kmp_finds_single_occurrence():
    assert kmp_search("hello world", "world") == [6]

def test_kmp_finds_multiple_non_overlapping_occurrences():
    assert kmp_search("abcabcabc", "abc") == [0, 3, 6]

def test_kmp_finds_overlapping_occurrences():
    assert kmp_search("aaaa", "aa") == [0, 1, 2]

def test_kmp_pattern_not_found():
    assert kmp_search("hello world", "xyz") == []

def test_kmp_empty_pattern_returns_empty():
    assert kmp_search("hello", "") == []

def test_kmp_pattern_longer_than_text():
    assert kmp_search("hi", "hello") == []

def test_kmp_pattern_at_very_start_and_end():
    assert kmp_search("abcXabc", "abc") == [0, 4]

def test_rabin_karp_matches_kmp_on_repeated_patterns():
    text = "abcabcabcabc"
    pattern = "abcabc"
    assert rabin_karp_search(text, pattern) == kmp_search(text, pattern)

def test_rabin_karp_pattern_not_found():
    assert rabin_karp_search("hello world", "xyz") == []

def test_rabin_karp_empty_or_oversized_pattern():
    assert rabin_karp_search("hello", "") == []
    assert rabin_karp_search("hi", "hello") == []

def test_rabin_karp_agrees_with_kmp_on_random_text():
    random.seed(7)
    alphabet = "ab"  

    for _ in range(30):
        text = "".join(random.choices(alphabet, k=50))
        pattern = "".join(random.choices(alphabet, k=random.randint(1, 5)))
        assert rabin_karp_search(text, pattern) == kmp_search(text, pattern)