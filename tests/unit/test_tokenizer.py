from search_engine.core.preprocessing.tokenizer import Tokenizer


def test_tokenizer_splits_on_punctuation_and_lowercases():
    tokenizer = Tokenizer()
    result = tokenizer.tokenize("Search-Engines, are FUN! (really?)")
    assert result == ["search", "engines", "are", "fun", "really"]


def test_tokenizer_handles_numbers():
    tokenizer = Tokenizer()
    result = tokenizer.tokenize("Python 3.12 released in 2023")
    assert result == ["python", "3", "12", "released", "in", "2023"]


def test_tokenizer_empty_string():
    assert Tokenizer().tokenize("") == []


def test_tokenizer_only_punctuation():
    assert Tokenizer().tokenize("!!! --- ,,,") == []