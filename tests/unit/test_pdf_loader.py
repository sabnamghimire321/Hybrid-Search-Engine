from pathlib import Path

import pytest
from reportlab.pdfgen import canvas

from search_engine.core.document import SourceType
from search_engine.core.loaders.pdf_loader import PdfLoader


def _make_pdf(path: Path, text: str) -> None:
    """Test helper: generates a minimal real PDF with reportlab so we
    exercise actual PDF parsing, not a mock."""
    c = canvas.Canvas(str(path))
    c.drawString(100, 750, text)
    c.save()


def test_pdf_loader_extracts_text(tmp_path: Path):
    pdf_path = tmp_path / "sample.pdf"
    _make_pdf(pdf_path, "Hello from a real PDF")

    loader = PdfLoader()
    assert loader.supports(pdf_path) is True

    doc = loader.load(pdf_path, doc_id=1)
    assert doc.source_type == SourceType.PDF
    assert "Hello from a real PDF" in doc.raw_text


def test_pdf_loader_rejects_non_pdf_extension():
    loader = PdfLoader()
    assert loader.supports(Path("notes.txt")) is False


def test_pdf_loader_raises_on_missing_file():
    loader = PdfLoader()
    with pytest.raises(FileNotFoundError):
        loader.load("/nonexistent.pdf", doc_id=1)