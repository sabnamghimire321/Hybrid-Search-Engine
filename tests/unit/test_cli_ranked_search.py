from pathlib import Path

from search_engine.cli.main import SearchEngineCLI

def _make_corpus(tmp_path: Path) -> Path:
    (tmp_path / "python_guide.txt").write_text(
        "Python is a great programming language. "
        "Python is widely used for search engines and web development. "
        "Many developers love python for its readability."
    )
    (tmp_path / "java_notes.txt").write_text(
        "Java is a popular programming language used in large enterprises."
    )
    (tmp_path / "notes.md").write_text("# Notes\nJust some markdown notes, no python here.")
    return tmp_path


def test_search_ranked_returns_scored_results(tmp_path):
    corpus = _make_corpus(tmp_path)
    engine = SearchEngineCLI()
    engine.index_directory(str(corpus))

    results = engine.search_ranked("python programming")
    assert len(results) >= 1
    assert results[0]["title"] == "python_guide"
    assert results[0]["score"] > 0

def test_search_ranked_scores_are_sorted_descending(tmp_path):
    corpus = _make_corpus(tmp_path)
    engine = SearchEngineCLI()
    engine.index_directory(str(corpus))

    results = engine.search_ranked("programming language")
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)

def test_search_ranked_includes_snippet_with_matched_word(tmp_path):
    corpus = _make_corpus(tmp_path)
    engine = SearchEngineCLI()
    engine.index_directory(str(corpus))

    results = engine.search_ranked("readability")
    assert len(results) == 1
    assert "readability" in results[0]["snippet"].lower()

def test_search_ranked_score_breakdown_present(tmp_path):
    corpus = _make_corpus(tmp_path)
    engine = SearchEngineCLI()
    engine.index_directory(str(corpus))

    results = engine.search_ranked("python programming")
    top = results[0]
    assert "python" in top["score_breakdown"] or "program" in top["score_breakdown"]
    assert sum(top["score_breakdown"].values()) == top["score"]

def test_search_ranked_filters_by_source_type(tmp_path):
    corpus = _make_corpus(tmp_path)
    engine = SearchEngineCLI()
    engine.index_directory(str(corpus))

    all_results = engine.search_ranked("programming")
    txt_only = engine.search_ranked("programming", source_type="txt")

    assert len(txt_only) == len(all_results)
    assert all(r["source_type"] == "txt" for r in txt_only)


def test_search_ranked_filter_excludes_non_matching_type(tmp_path):
    corpus = _make_corpus(tmp_path)
    engine = SearchEngineCLI()
    engine.index_directory(str(corpus))
    results = engine.search_ranked("engines", source_type="markdown")
    assert results == []


def test_search_ranked_respects_top_k(tmp_path):
    corpus = _make_corpus(tmp_path)
    engine = SearchEngineCLI()
    engine.index_directory(str(corpus))

    results = engine.search_ranked("programming language", top_k=1)
    assert len(results) == 1


def test_search_ranked_no_matches_returns_empty_list(tmp_path):
    corpus = _make_corpus(tmp_path)
    engine = SearchEngineCLI()
    engine.index_directory(str(corpus))

    assert engine.search_ranked("nonexistentword") == []


def test_suggest_returns_matching_prefixes(tmp_path):
    corpus = _make_corpus(tmp_path)
    engine = SearchEngineCLI()
    engine.index_directory(str(corpus))

    suggestions = engine.suggest("pyth")
    assert "python" in suggestions


def test_suggest_is_case_insensitive(tmp_path):
    corpus = _make_corpus(tmp_path)
    engine = SearchEngineCLI()
    engine.index_directory(str(corpus))

    suggestions = engine.suggest("PYTH")
    assert "python" in suggestions


def test_suggest_respects_limit(tmp_path):
    corpus = _make_corpus(tmp_path)
    engine = SearchEngineCLI()
    engine.index_directory(str(corpus))

    suggestions = engine.suggest("p", limit=2)
    assert len(suggestions) <= 2


def test_suggest_no_match_returns_empty(tmp_path):
    corpus = _make_corpus(tmp_path)
    engine = SearchEngineCLI()
    engine.index_directory(str(corpus))

    assert engine.suggest("zzzzz") == []

def test_suggest_uses_unstemmed_words_not_stemmed_forms(tmp_path):
    corpus = _make_corpus(tmp_path)
    engine = SearchEngineCLI()
    engine.index_directory(str(corpus))

    suggestions = engine.suggest("programm")
    assert "programming" in suggestions