from search_engine.algorithms.edit_distance import levenshtein_distance

def test_classic_kitten_sitting_example():
    assert levenshtein_distance("kitten", "sitting") == 3

def test_identical_strings_have_zero_distance():
    assert levenshtein_distance("python", "python") == 0

def test_empty_string_distance_equals_other_length():
    assert levenshtein_distance("", "hello") == 5
    assert levenshtein_distance("hello", "") == 5
    assert levenshtein_distance("", "") == 0

def test_single_substitution():
    assert levenshtein_distance("cat", "bat") == 1

def test_single_insertion():
    assert levenshtein_distance("cat", "cats") == 1

def test_single_deletion():
    assert levenshtein_distance("cats", "cat") == 1

def test_completely_different_strings():
    assert levenshtein_distance("abc", "xyz") == 3

def test_typo_correction_use_case():
    assert levenshtein_distance("pyhton", "python") == 2  
    assert levenshtein_distance("serach", "search") == 2
    assert levenshtein_distance("enigne", "engine") == 2

def test_distance_is_symmetric():
    assert levenshtein_distance("kitten", "sitting") == levenshtein_distance("sitting", "kitten")