"""
Abstract base class defining the DocumentLoader interface.

Phase 1

Design decision: each concrete loader (txt/pdf/html/markdown) only needs to
implement `extract_text`. `load` (the public API) is shared and handles
doc_id assignment + wrapping into a `Document`, so that logic exists in
exactly one place instead of being duplicated four times.

Time complexity: O(1) here — actual extraction cost lives in each subclass
and is documented there (e.g. PDF parsing is O(pages), HTML parsing is
O(markup length)).
"""

from abc import ABC, abstractmethod
from pathlib import Path

from search_engine.core.document import Document, SourceType


class DocumentLoader(ABC):
    """Base interface every file-type loader must implement."""

    source_type: SourceType

    @abstractmethod
    def extract_text(self, path: Path) -> str:
        """Read `path` and return its plain-text content.

        Subclasses implement only this method. Must raise on unreadable /
        malformed files rather than silently returning an empty string, so
        the caller can decide whether to skip or fail the whole indexing run.
        """
        raise NotImplementedError

    def supports(self, path: Path) -> bool:
        """Whether this loader can handle the given file, based on
        extension. Subclasses may override for content-sniffing instead."""
        raise NotImplementedError

    def load(self, path: str | Path, doc_id: int) -> Document:
        """Public entry point: extract text and wrap it in a Document.

        Raises:
            FileNotFoundError: if `path` doesn't exist.
            ValueError: if extraction produces no usable text.
        """
        resolved = Path(path)
        if not resolved.exists():
            raise FileNotFoundError(f"No such file: {resolved}")

        text = self.extract_text(resolved)
        return Document.from_path(
            doc_id=doc_id,
            path=str(resolved),
            source_type=self.source_type,
            raw_text=text,
        )
