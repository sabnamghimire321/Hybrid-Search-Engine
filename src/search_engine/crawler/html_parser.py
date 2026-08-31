from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from search_engine.core.loaders.html_loader import HtmlLoader

def extract_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []
    seen_on_this_page: set[str] = set()

    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if not href:
            continue

        absolute_url = urljoin(base_url, href)
        parsed = urlparse(absolute_url)

        if parsed.scheme not in ("http", "https"):
            continue

        normalized = parsed._replace(fragment="").geturl()

        if normalized in seen_on_this_page:
            continue
        seen_on_this_page.add(normalized)
        links.append(normalized)

    return links

def extract_title(html: str) -> str | None:
    return HtmlLoader.extract_title(html)