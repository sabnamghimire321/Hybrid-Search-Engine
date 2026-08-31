from search_engine.crawler.crawler import Crawler, MockFetcher

def _build_fixture_web() -> MockFetcher:
    pages = {
        "https://example.com/": (
            '<a href="/about">About</a>'
            '<a href="/blog/post1">Blog</a>'
            '<a href="/admin/secret">Admin</a>'
            '<a href="https://external.com/page">External</a>'
            '<a href="/broken-link">Broken</a>'
        ),
        "https://example.com/about": (
            '<a href="/">Home</a><a href="/contact">Contact</a>'
        ),
        "https://example.com/blog/post1": '<a href="/blog/post2">Next</a>',
        "https://example.com/blog/post2": "<p>End of the blog chain, no links.</p>",
        "https://example.com/contact": "<title>Contact Us</title><p>Get in touch.</p>",
        "https://example.com/admin/secret": "<p>Should never be fetched.</p>",
        "https://external.com/page": "<title>External Page</title><p>Hello.</p>",
    }
    robots_txt = {
        "example.com": "User-agent: *\nDisallow: /admin/",
        "external.com": "",
    }
    return MockFetcher(pages, robots_txt)

def test_crawl_visits_all_reachable_allowed_pages():
    crawler = Crawler(_build_fixture_web(), user_agent="TestBot", default_delay=0.0)
    crawler.crawl(["https://example.com/"])

    assert "https://example.com/" in crawler.page_content
    assert "https://example.com/about" in crawler.page_content
    assert "https://example.com/blog/post1" in crawler.page_content
    assert "https://example.com/blog/post2" in crawler.page_content
    assert "https://example.com/contact" in crawler.page_content
    assert "https://external.com/page" in crawler.page_content

def test_robots_txt_disallowed_page_is_never_fetched():
    crawler = Crawler(_build_fixture_web(), user_agent="TestBot", default_delay=0.0)
    crawler.crawl(["https://example.com/"])

    assert "https://example.com/admin/secret" not in crawler.page_content

def test_broken_link_is_skipped_without_crashing():
    crawler = Crawler(_build_fixture_web(), user_agent="TestBot", default_delay=0.0)
    crawler.crawl(["https://example.com/"])

    assert "https://example.com/broken-link" not in crawler.page_content

def test_cyclic_links_do_not_cause_infinite_crawl():
    crawler = Crawler(_build_fixture_web(), user_agent="TestBot", default_delay=0.0)
    crawler.crawl(["https://example.com/"])

    assert crawler.pages_crawled == 6

def test_graph_records_link_structure():
    crawler = Crawler(_build_fixture_web(), user_agent="TestBot", default_delay=0.0)
    crawler.crawl(["https://example.com/"])

    assert crawler.graph.has_edge("https://example.com/", "https://example.com/about")
    assert crawler.graph.has_edge("https://example.com/about", "https://example.com/contact")
    assert crawler.graph.has_edge("https://example.com/blog/post1", "https://example.com/blog/post2")

def test_titles_are_extracted_when_present():
    crawler = Crawler(_build_fixture_web(), user_agent="TestBot", default_delay=0.0)
    crawler.crawl(["https://example.com/"])

    assert crawler.page_titles["https://example.com/contact"] == "Contact Us"
    assert crawler.page_titles["https://external.com/page"] == "External Page"
    assert "https://example.com/" not in crawler.page_titles

def test_max_pages_limits_crawl_size():
    crawler = Crawler(
        _build_fixture_web(), user_agent="TestBot", default_delay=0.0, max_pages=2
    )
    crawler.crawl(["https://example.com/"])

    assert crawler.pages_crawled == 2

def test_crawled_urls_matches_page_content_keys():
    crawler = Crawler(_build_fixture_web(), user_agent="TestBot", default_delay=0.0)
    crawler.crawl(["https://example.com/"])

    assert set(crawler.crawled_urls()) == set(crawler.page_content.keys())

def test_robots_txt_is_fetched_once_per_domain_not_per_page():
    class CountingFetcher(MockFetcher):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.robots_fetch_count = 0

        def fetch_robots_txt(self, domain: str) -> str:
            self.robots_fetch_count += 1
            return super().fetch_robots_txt(domain)

    pages = {
        "https://example.com/": '<a href="/about">About</a>',
        "https://example.com/about": '<a href="/contact">Contact</a>',
        "https://example.com/contact": "<p>End</p>",
    }
    fetcher = CountingFetcher(pages, {"example.com": "User-agent: *\n"})
    crawler = Crawler(fetcher, user_agent="TestBot", default_delay=0.0)
    crawler.crawl(["https://example.com/"])

    assert fetcher.robots_fetch_count == 1