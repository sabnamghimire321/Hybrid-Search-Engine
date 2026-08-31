from search_engine.core.preprocessing.stopwords import StopwordFilter


def test_removes_common_stopwords():
    f = StopwordFilter()
    result = f.remove(["the", "cat", "sat", "on", "the", "mat"])
    assert result == ["cat", "sat", "mat"]


def test_keeps_all_tokens_if_no_stopwords_present():
    f = StopwordFilter()
    result = f.remove(["python", "search", "engine"])
    assert result == ["python", "search", "engine"]


def test_empty_list():
    assert StopwordFilter().remove([]) == []


def test_is_stopword():
    f = StopwordFilter()
    assert f.is_stopword("the") is True
    assert f.is_stopword("python") is False