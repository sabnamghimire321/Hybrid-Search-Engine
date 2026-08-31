"""
Document data model shared across loaders, indexing, and ranking.

Phase 1

Every loader (txt/pdf/html/markdown) and, later, the web crawler (Phase 6)
produce `Document` instances. Everything downstream — preprocessing, the
inverted index, ranking — depends only on this interface, not on how the
document was obtained.

Time complexity: O(1) for all operations here (attribute access / simple
list appends). The class itself does no processing — it's a plain data
carrier by design, so indexing logic can't leak into it.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class SourceType(str, Enum):
    """Where a Document's content originally came from."""

    TXT = "txt"
    PDF = "pdf"
    HTML = "html"
    MARKDOWN = "markdown"
    WEB = "web"


@dataclass
class Document:
    """
    A single document in the corpus.

    Attributes:
        doc_id: Stable unique identifier. Assigned by the caller (e.g. the
            indexer) rather than generated here, so re-indexing the same
            file path always yields the same doc_id.
        source_path: Original file path (or URL, once the crawler exists).
        source_type: Which loader produced this document.
        title: Best-effort title (filename stem, <title> tag, first H1, etc).
            Loaders decide how to populate this.
        raw_text: Full extracted text, before any tokenization/normalization.
        metadata: Free-form extra info a loader wants to attach (e.g. PDF
            page count, HTML meta tags). Not used by the core index, but
            kept around for ranking/display later.
    """

    doc_id: int
    source_path: str
    source_type: SourceType
    title: str
    raw_text: str
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.raw_text.strip():
            raise ValueError(f"Document {self.doc_id} ({self.source_path}) has no text content")

    @property
    def word_count(self) -> int:
        """Rough word count of raw_text. O(n) in text length."""
        return len(self.raw_text.split())

    @classmethod
    def from_path(
        cls,
        doc_id: int,
        path: str,
        source_type: SourceType,
        raw_text: str,
        title: str | None = None,
        metadata: dict | None = None,
    ) -> "Document":
        """Convenience constructor: derives a default title from the filename
        if the loader doesn't supply one."""
        resolved_title = title if title else Path(path).stem
        return cls(
            doc_id=doc_id,
            source_path=path,
            source_type=source_type,
            title=resolved_title,
            raw_text=raw_text,
            metadata=metadata or {},
        )

    def __repr__(self) -> str:
        preview = self.raw_text[:50].replace("\n", " ")
        return f"Document(id={self.doc_id}, title={self.title!r}, preview={preview!r}...)"
