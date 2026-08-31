from urllib.parse import urlparse

from search_engine.crawler.html_parser import extract_links, extract_title
from search_engine.crawler.robots import RobotsParser
from search_engine.crawler.scheduler import CrawlScheduler
from search_engine.crawler.url_frontier import UrlFrontier
from search_engine.datastructures.graph import Graph

class MockFetcher:
    def __init__(self, pages: dict[str, str], robots_txt: dict[str, str] | None = None) -> None:
        self._pages = pages
        self._robots_txt = robots_txt or {}

    def fetch(self, url: str) -> str | None:
        """Returns the page's HTML, or None if the URL isn't in the
        fixture (simulating a 404 / failed fetch)."""
        return self._pages.get(url)

    def fetch_robots_txt(self, domain: str) -> str:
        return self._robots_txt.get(domain, "")

class Crawler:
    def __init__(
        self,
        fetcher,
        user_agent: str = "SearchEngineBot",
        default_delay: float = 1.0,
        max_pages: int | None = None,
    ) -> None:
        self._fetcher = fetcher
        self._user_agent = user_agent
        self._frontier = UrlFrontier()
        self._scheduler = CrawlScheduler(default_delay=default_delay)
        self._robots_cache: dict[str, RobotsParser] = {}
        self._max_pages = max_pages

        self.graph = Graph(directed=True)
        self.page_content: dict[str, str] = {}
        self.page_titles: dict[str, str] = {}

    def _domain_of(self, url: str) -> str:
        return urlparse(url).netloc

    def _robots_for(self, domain: str) -> RobotsParser:
        if domain not in self._robots_cache:
            robots_txt = self._fetcher.fetch_robots_txt(domain)
            self._robots_cache[domain] = RobotsParser(robots_txt, user_agent=self._user_agent)
        return self._robots_cache[domain]

    def crawl(self, seed_urls: list[str]) -> None:
        for url in seed_urls:
            self._frontier.add(url)

        pages_crawled = 0

        while self._frontier.has_next():
            if self._max_pages is not None and pages_crawled >= self._max_pages:
                break

            url = self._frontier.next()
            domain = self._domain_of(url)
            robots = self._robots_for(domain)

            path = urlparse(url).path or "/"
            if not robots.is_allowed(path):
                continue

            if robots.crawl_delay is not None:
                self._scheduler.set_domain_delay(domain, robots.crawl_delay)
            self._scheduler.wait_if_needed(domain)

            html = self._fetcher.fetch(url)
            if html is None:
                continue

            self.graph.add_node(url)
            self.page_content[url] = html
            title = extract_title(html)
            if title:
                self.page_titles[url] = title

            for link in extract_links(html, base_url=url):
                self.graph.add_edge(url, link)
                self._frontier.add(link)

            pages_crawled += 1

    @property
    def pages_crawled(self) -> int:
        return len(self.page_content)

    def crawled_urls(self) -> list[str]:
        return list(self.page_content.keys())