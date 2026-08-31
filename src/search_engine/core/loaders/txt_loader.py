"""
Loader for plain .txt files.

Phase 1

Simplest possible loader — establishes the pattern that pdf_loader,
html_loader, and markdown_loader all follow: implement `extract_text`,
inherit everything else from DocumentLoader.

Time complexity: O(n) in file size (single read).
"""

from pathlib import Path

from search_engine.core.document import SourceType
from search_engine.core.loaders.base import DocumentLoader


class TxtLoader(DocumentLoader):
    source_type = SourceType.TXT

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() == ".txt"

    def extract_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="replace")
