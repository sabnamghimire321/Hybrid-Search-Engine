from pathlib import Path

from search_engine.cli.main import SearchEngineCLI


def _make_corpus(tmp_path: Path) -> Path:
    (tmp_path / "python_guide.txt").write_text(
        "Python is a great programming language for search engines."
    )
    (tmp_path / "java_notes.txt").write_text(
        "Java is also a popular programming language used in enterprises."
    )
    (tmp_path / "ml.md").write_text(
        "# Machine Learning Basics\n\nMachine learning is a subset of artificial intelligence."
    )
    (tmp_path / "data.csv").write_text("col1,col2\n1,2\n")
    return tmp_path


def test_index_directory_counts_supported_files_only(tmp_path: Path):
    corpus = _make_corpus(tmp_path)
    engine = SearchEngineCLI()

    count = engine.index_directory(str(corpus))

    assert count == 3  
    assert engine.document_count == 3


def test_search_bare_words_defaults_to_and(tmp_path: Path):
    corpus = _make_corpus(tmp_path)
    engine = SearchEngineCLI()
    engine.index_directory(str(corpus))

    results = engine.search("programming language")
    titles = {title for _, title, _ in results}
    assert titles == {"python_guide", "java_notes"}


def test_search_with_explicit_or(tmp_path: Path):
    corpus = _make_corpus(tmp_path)
    engine = SearchEngineCLI()
    engine.index_directory(str(corpus))

    results = engine.search("python OR machine")
    titles = {title for _, title, _ in results}
    assert titles == {"python_guide", "Machine Learning Basics"}


def test_search_with_not(tmp_path: Path):
    corpus = _make_corpus(tmp_path)
    engine = SearchEngineCLI()
    engine.index_directory(str(corpus))

    results = engine.search("programming NOT java")
    titles = {title for _, title, _ in results}
    assert titles == {"python_guide"}


def test_search_exact_phrase(tmp_path: Path):
    corpus = _make_corpus(tmp_path)
    engine = SearchEngineCLI()
    engine.index_directory(str(corpus))

    results = engine.search('"machine learning"')
    assert len(results) == 1
    assert results[0][1] == "Machine Learning Basics"


def test_search_no_results_returns_empty_list(tmp_path: Path):
    corpus = _make_corpus(tmp_path)
    engine = SearchEngineCLI()
    engine.index_directory(str(corpus))

    assert engine.search("nonexistentword") == []


def test_index_directory_raises_on_missing_folder():
    engine = SearchEngineCLI()
    try:
        engine.index_directory("/definitely/not/a/real/folder")
        assert False, "should have raised"
    except FileNotFoundError:
        pass