from fastapi.testclient import TestClient

from search_engine.cli.main import SearchEngineCLI
from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.core.preprocessing.pipeline import Pipeline
from search_engine.storage.persistent_index import PersistentIndexStore

def _build_realistic_corpus(tmp_path):
    (tmp_path / "python_intro.txt").write_text(
        "Python is a high-level programming language known for its readability. "
        "Python supports multiple programming paradigms including object-oriented "
        "and functional programming. Many developers choose Python for data science."
    )
    (tmp_path / "web_development.txt").write_text(
        "Web development involves building websites and web applications. "
        "Popular languages for web development include JavaScript, Python, and Ruby. "
        "Frontend frameworks like React make building user interfaces easier."
    )
    (tmp_path / "cooking.md").write_text(
        "# Italian Cooking\n\n"
        "Italian cuisine emphasizes fresh, simple ingredients. "
        "Pasta dishes are a cornerstone of Italian cooking traditions."
    )
    return tmp_path


def test_full_indexing_and_search_pipeline(tmp_path):
    corpus = _build_realistic_corpus(tmp_path)
    engine = SearchEngineCLI()

    indexed_count = engine.index_directory(str(corpus))
    assert indexed_count == 3

    boolean_results = engine.search("python")
    assert len(boolean_results) == 2

    ranked_results = engine.search_ranked("python programming")
    assert len(ranked_results) >= 1
    assert ranked_results[0]["title"] == "python_intro"
    assert "score_breakdown" in ranked_results[0]
    assert "snippet" in ranked_results[0]

    cross_topic_results = engine.search_ranked("pasta italian")
    assert len(cross_topic_results) == 1
    assert cross_topic_results[0]["title"] == "cooking"

    suggestions = engine.suggest("prog")
    assert "programming" in suggestions

    md_only = engine.search_ranked("cooking", source_type="markdown")
    assert len(md_only) == 1
    assert md_only[0]["source_type"] == "markdown"

def test_persistence_roundtrip_preserves_search_behavior(tmp_path):
    corpus = _build_realistic_corpus(tmp_path)

    pipeline = Pipeline()
    original_index = InvertedIndex()
    doc_id = 1
    for path in sorted(corpus.glob("*")):
        if path.suffix in (".txt", ".md"):
            text = path.read_text()
            tokens = pipeline.process(text)
            original_index.add_document(doc_id, tokens)
            doc_id += 1

    store = PersistentIndexStore()
    save_path = tmp_path / "index.bin"
    store.save(original_index, str(save_path))
    restored_index = store.load(str(save_path))

    for term in original_index.all_terms():
        assert restored_index.get_postings(term) == original_index.get_postings(term)

    assert restored_index.document_count == original_index.document_count

def test_api_full_session_flow(tmp_path):
    corpus = _build_realistic_corpus(tmp_path)

    from search_engine.api.main import create_app

    app = create_app(engine=SearchEngineCLI())
    client = TestClient(app)
    auth_headers = {"X-API-Key": "dev-key-change-me"}

    index_response = client.post(
        "/index", params={"directory": str(corpus)}, headers=auth_headers
    )
    assert index_response.status_code == 200
    assert index_response.json()["indexed"] == 3

    search_response = client.get(
        "/search", params={"q": "python programming"}, headers=auth_headers
    )
    assert search_response.status_code == 200
    body = search_response.json()
    assert body["count"] >= 1
    assert body["results"][0]["title"] == "python_intro"
    assert "snippet" in body["results"][0]

    suggest_response = client.get("/suggest", params={"prefix": "prog"})
    assert "programming" in suggest_response.json()["suggestions"]

    client.get("/search", params={"q": "cooking"})

    history_response = client.get("/history", headers=auth_headers)
    assert history_response.json()["total_queries"] == 1

    analytics_response = client.get("/analytics", headers=auth_headers)
    analytics_body = analytics_response.json()
    assert analytics_body["total_queries"] == 2

def test_crawler_output_feeds_into_a_searchable_index():
    from search_engine.crawler.crawler import Crawler, MockFetcher

    pages = {
        "https://example.com/": '<a href="/about">About</a> Welcome to our python tutorials site.',
        "https://example.com/about": "<title>About</title> We teach python programming online.",
    }
    fetcher = MockFetcher(pages, robots_txt={"example.com": ""})
    crawler = Crawler(fetcher, default_delay=0.0)
    crawler.crawl(["https://example.com/"])

    assert crawler.pages_crawled == 2

    pipeline = Pipeline()
    index = InvertedIndex()
    for i, (url, html) in enumerate(crawler.page_content.items(), start=1):
        import re

        text_only = re.sub(r"<[^>]+>", " ", html)
        index.add_document(i, pipeline.process(text_only))

    assert index.document_frequency("python") == 2
    assert index.document_count == 2