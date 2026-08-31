from pathlib import Path

from bs4 import BeautifulSoup

from search_engine.core.document import Document, SourceType
from search_engine.core.loaders.base import DocumentLoader


class HtmlLoader(DocumentLoader):
    source_type = SourceType.HTML

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() in (".html", ".htm")

    @staticmethod
    def strip_html_to_text(raw_html: str) -> str:
        soup = BeautifulSoup(raw_html, "html.parser")

        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        return "\n".join(line.strip() for line in text.splitlines() if line.strip())

    @staticmethod
    def extract_title(raw_html: str) -> str | None:
        """Pure function: HTML string -> <title> text, or None."""
        soup = BeautifulSoup(raw_html, "html.parser")
        title_tag = soup.find("title")
        if title_tag and title_tag.get_text().strip():
            return title_tag.get_text().strip()
        return None

    def extract_text(self, path: Path) -> str:
        raw_html = path.read_text(encoding="utf-8", errors="replace")
        text = self.strip_html_to_text(raw_html)
        if not text:
            raise ValueError(f"No visible text content in {path}")
        return text

    def load(self, path: str | Path, doc_id: int) -> Document:
        resolved = Path(path)
        if not resolved.exists():
            raise FileNotFoundError(f"No such file: {resolved}")

        raw_html = resolved.read_text(encoding="utf-8", errors="replace")
        title = self.extract_title(raw_html)
        text = self.extract_text(resolved)

        return Document.from_path(
            doc_id=doc_id,
            path=str(resolved),
            source_type=self.source_type,
            raw_text=text,
            title=title,
        )