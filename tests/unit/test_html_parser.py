from search_engine.crawler.html_parser import extract_links, extract_title

def test_extracts_absolute_links():
    html = '<a href="https://example.com/page1">Page 1</a>'
    links = extract_links(html, base_url="https://example.com")
    assert links == ["https://example.com/page1"]

def test_resolves_relative_links_against_base_url():
    html = """
    <a href="/about">About</a>
    <a href="contact.html">Contact</a>
    <a href="../parent-page">Parent</a>
    """
    links = extract_links(html, base_url="https://example.com/blog/post1")

    assert "https://example.com/about" in links
    assert "https://example.com/blog/contact.html" in links
    assert "https://example.com/parent-page" in links

def test_filters_out_non_crawlable_schemes():
    html = """
    <a href="mailto:someone@example.com">Email</a>
    <a href="javascript:void(0)">JS link</a>
    <a href="tel:+1234567890">Call</a>
    <a href="https://example.com/real-page">Real page</a>
    """
    links = extract_links(html, base_url="https://example.com")
    assert links == ["https://example.com/real-page"]

def test_strips_url_fragments():
    html = """
    <a href="page.html#intro">Intro</a>
    <a href="page.html#conclusion">Conclusion</a>
    """
    links = extract_links(html, base_url="https://example.com")
    assert links == ["https://example.com/page.html"]

def test_duplicate_links_on_same_page_are_deduped():
    html = """
    <a href="https://example.com/x">First mention</a>
    <a href="https://example.com/x">Second mention</a>
    """
    links = extract_links(html, base_url="https://example.com")
    assert links == ["https://example.com/x"]

def test_empty_href_is_skipped():
    html = '<a href="">Empty link</a><a href="https://example.com/real">Real</a>'
    links = extract_links(html, base_url="https://example.com")
    assert links == ["https://example.com/real"]


def test_no_links_returns_empty_list():
    html = "<p>Just a paragraph, no links here.</p>"
    assert extract_links(html, base_url="https://example.com") == []

def test_extract_title_delegates_correctly():
    html = "<html><head><title>My Crawled Page</title></head><body></body></html>"
    assert extract_title(html) == "My Crawled Page"

def test_extract_title_returns_none_when_absent():
    html = "<html><body><p>No title tag here</p></body></html>"
    assert extract_title(html) is None

def test_preserves_first_seen_order():
    html = """
    <a href="https://example.com/c">C</a>
    <a href="https://example.com/a">A</a>
    <a href="https://example.com/b">B</a>
    """
    links = extract_links(html, base_url="https://example.com")
    assert links == ["https://example.com/c", "https://example.com/a", "https://example.com/b"]