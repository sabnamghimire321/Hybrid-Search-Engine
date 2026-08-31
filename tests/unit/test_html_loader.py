from pathlib import Path

import pytest

from search_engine.core.document import SourceType
from search_engine.core.loaders.html_loader import HtmlLoader


SAMPLE_HTML = """
<html>
<head><title>My Test Page</title>
<style>body { color: red; }</style>
</head>
<body>
<h1>Welcome</h1>
<p>This is a paragraph about search engines.</p>
<script>console.log("should not appear in text");</script>
</body>
</html>
"""


def test_html_loader_extracts_title_and_text(tmp_path: Path):
    f = tmp_path / "page.html"
    f.write_text(SAMPLE_HTML)

    loader = HtmlLoader()
    assert loader.supports(f) is True

    doc = loader.load(f, doc_id=1)
    assert doc.source_type == SourceType.HTML
    assert doc.title == "My Test Page"
    assert "search engines" in doc.raw_text
    assert "console.log" not in doc.raw_text
    assert "color: red" not in doc.raw_text


def test_html_loader_falls_back_to_filename_when_no_title(tmp_path: Path):
    f = tmp_path / "untitled.html"
    f.write_text("<html><body><p>no title tag here</p></body></html>")

    doc = HtmlLoader().load(f, doc_id=2)
    assert doc.title == "untitled"


def test_html_loader_raises_on_missing_file():
    with pytest.raises(FileNotFoundError):
        HtmlLoader().load("/nonexistent.html", doc_id=1)