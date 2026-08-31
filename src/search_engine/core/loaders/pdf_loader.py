from pathlib import Path

from pypdf import PdfReader

from search_engine.core.document import SourceType
from search_engine.core.loaders.base import DocumentLoader


class PdfLoader(DocumentLoader):
    source_type = SourceType.PDF

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() == ".pdf"

    def extract_text(self, path: Path) -> str:
        reader = PdfReader(str(path))

        page_texts = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(page_texts)

        if not text.strip():
            raise ValueError(
                f"No extractable text in {path} — likely a scanned/image-only PDF (needs OCR)"
            )
        return text
