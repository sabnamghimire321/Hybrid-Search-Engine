from pathlib import Path

import pytest

from search_engine.core.document import SourceType
from search_engine.core.loaders.markdown_loader import MarkdownLoader


SAMPLE_MD = """# My Markdown Doc

This is a **paragraph** about search engines.

- point one
- point two

```python
this_is_code = "should still become plain text, that's fine"
```
"""


def test_markdown_loader_extracts_title_and_text(tmp_path: Path):
    f = tmp_path / "notes.md"
    f.write_text(SAMPLE_MD)

    loader = MarkdownLoader()
    assert loader.supports(f) is True

    doc = loader.load(f, doc_id=1)
    assert doc.source_type == SourceType.MARKDOWN
    assert doc.title == "My Markdown Doc"
    assert "paragraph" in doc.raw_text
    assert "search engines" in doc.raw_text
    assert "point one" in doc.raw_text


def test_markdown_loader_falls_back_to_filename_when_no_h1(tmp_path: Path):
    f = tmp_path / "untitled.md"
    f.write_text("Just a plain paragraph, no heading.")

    doc = MarkdownLoader().load(f, doc_id=2)
    assert doc.title == "untitled"


def test_markdown_loader_raises_on_missing_file():
    with pytest.raises(FileNotFoundError):
        MarkdownLoader().load("/nonexistent.md", doc_id=1)