from pathlib import Path

import markdown as md

from search_engine.core.document import Document, SourceType
from search_engine.core.loaders.base import DocumentLoader
from search_engine.core.loaders.html_loader import HtmlLoader


class MarkdownLoader(DocumentLoader):
    source_type = SourceType.MARKDOWN

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() in (".md", ".markdown")

    def extract_text(self, path: Path) -> str:
        raw_md = path.read_text(encoding="utf-8", errors="replace")
        html = md.markdown(raw_md)
        text = HtmlLoader.strip_html_to_text(html)

        if not text:
            raise ValueError(f"No text content in {path}")
        return text

    def _extract_h1_title(self, raw_md: str) -> str | None:
        for line in raw_md.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped[2:].strip()
        return None

    def load(self, path: str | Path, doc_id: int) -> Document:
        resolved = Path(path)
        if not resolved.exists():
            raise FileNotFoundError(f"No such file: {resolved}")

        raw_md = resolved.read_text(encoding="utf-8", errors="replace")
        title = self._extract_h1_title(raw_md)
        text = self.extract_text(resolved)

        return Document.from_path(
            doc_id=doc_id,
            path=str(resolved),
            source_type=self.source_type,
            raw_text=text,
            title=title,
        )