from pathlib import Path

import pytest

from search_engine.core.document import Document, SourceType
from search_engine.core.loaders.txt_loader import TxtLoader


def test_document_rejects_empty_text():
    with pytest.raises(ValueError):
        Document(
            doc_id=1,
            source_path="empty.txt",
            source_type=SourceType.TXT,
            title="empty",
            raw_text="   ",
        )


def test_document_from_path_derives_title_from_filename():
    doc = Document.from_path(
        doc_id=1,
        path="/some/dir/my-report.txt",
        source_type=SourceType.TXT,
        raw_text="hello world",
    )
    assert doc.title == "my-report"
    assert doc.word_count == 2


def test_txt_loader_loads_file(tmp_path: Path):
    f = tmp_path / "sample.txt"
    f.write_text("The quick brown fox jumps over the lazy dog.")

    loader = TxtLoader()
    assert loader.supports(f) is True

    doc = loader.load(f, doc_id=42)
    assert doc.doc_id == 42
    assert doc.source_type == SourceType.TXT
    assert doc.title == "sample"
    assert "quick brown fox" in doc.raw_text


def test_txt_loader_raises_on_missing_file():
    loader = TxtLoader()
    with pytest.raises(FileNotFoundError):
        loader.load("/nonexistent/path.txt", doc_id=1)
