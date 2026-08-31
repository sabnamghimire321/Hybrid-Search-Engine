import re
import sys
from dataclasses import dataclass
from pathlib import Path

from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.core.loaders.base import DocumentLoader
from search_engine.core.loaders.html_loader import HtmlLoader
from search_engine.core.loaders.markdown_loader import MarkdownLoader
from search_engine.core.loaders.pdf_loader import PdfLoader
from search_engine.core.loaders.txt_loader import TxtLoader
from search_engine.core.preprocessing.pipeline import Pipeline
from search_engine.core.preprocessing.tokenizer import Tokenizer
from search_engine.core.query.boolean_search import BooleanSearch
from search_engine.core.query.phrase_search import PhraseSearch
from search_engine.datastructures.trie import Trie
from search_engine.ranking.bm25 import BM25Ranker

_LOADERS: dict[str, DocumentLoader] = {
    ".txt": TxtLoader(),
    ".pdf": PdfLoader(),
    ".html": HtmlLoader(),
    ".htm": HtmlLoader(),
    ".md": MarkdownLoader(),
    ".markdown": MarkdownLoader(),
}

_QUERY_TOKEN_PATTERN = re.compile(r'"[^"]*"|\S+')


@dataclass
class _IndexedDocument:
    title: str
    source_path: str
    source_type: str
    raw_text: str


class SearchEngineCLI:
    def __init__(self) -> None:
        self._pipeline = Pipeline()
        self._tokenizer = Tokenizer()
        self._index = InvertedIndex()
        self._boolean_search = BooleanSearch(self._index, self._pipeline)
        self._phrase_search = PhraseSearch(self._index, self._pipeline)
        self._documents: dict[int, _IndexedDocument] = {}
        self._suggestion_trie = Trie()
        self._next_doc_id = 1

    @property
    def document_count(self) -> int:
        return self._index.document_count

    @property
    def vocabulary_size(self) -> int:
        return self._index.vocabulary_size

    def index_directory(self, directory: str) -> int:
        root = Path(directory)
        if not root.exists():
            raise FileNotFoundError(f"No such directory: {root}")

        count = 0
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            loader = _LOADERS.get(path.suffix.lower())
            if loader is None:
                continue

            try:
                doc = loader.load(path, doc_id=self._next_doc_id)
            except ValueError as e:
                print(f"  skipped {path.name}: {e}")
                continue

            tokens = self._pipeline.process(doc.raw_text)
            if not tokens:
                print(f"  skipped {path.name}: no indexable tokens after preprocessing")
                continue

            self._index.add_document(doc.doc_id, tokens)
            self._documents[doc.doc_id] = _IndexedDocument(
                title=doc.title,
                source_path=doc.source_path,
                source_type=str(doc.source_type.value),
                raw_text=doc.raw_text,
            )

            for word in self._tokenizer.tokenize(doc.raw_text):
                self._suggestion_trie.insert(word)

            self._next_doc_id += 1
            count += 1

        return count

    def search(self, query: str) -> list[tuple[int, str, str]]:
        doc_ids = self._execute_query(query)
        results = [
            (doc_id, self._documents[doc_id].title, self._documents[doc_id].source_path)
            for doc_id in doc_ids
        ]
        return sorted(results, key=lambda r: r[0])

    def search_ranked(
        self, query: str, source_type: str | None = None, top_k: int = 10
    ) -> list[dict]:
        candidate_ids = self._execute_query(query)

        if source_type is not None:
            candidate_ids = {
                doc_id
                for doc_id in candidate_ids
                if self._documents[doc_id].source_type == source_type
            }

        if not candidate_ids:
            return []

        ranker = BM25Ranker(self._index)
        query_terms = self._extract_content_terms(query)
        highlight_words = self._extract_raw_query_words(query)

        scored = []
        for doc_id in candidate_ids:
            doc = self._documents[doc_id]
            scored.append(
                {
                    "doc_id": doc_id,
                    "title": doc.title,
                    "path": doc.source_path,
                    "source_type": doc.source_type,
                    "score": ranker.score(query_terms, doc_id),
                    "score_breakdown": ranker.score_breakdown(query_terms, doc_id),
                    "snippet": self._make_snippet(doc.raw_text, highlight_words),
                }
            )

        scored.sort(key=lambda r: r["score"], reverse=True)
        return scored[:top_k]

    def suggest(self, prefix: str, limit: int = 10) -> list[str]:
        return self._suggestion_trie.autocomplete(prefix.lower(), limit=limit)

    def _extract_content_terms(self, query: str) -> list[str]:
        tokens = _QUERY_TOKEN_PATTERN.findall(query.strip())
        content_words = []
        for token in tokens:
            if token.upper() in ("AND", "OR", "NOT"):
                continue
            text = token[1:-1] if token.startswith('"') and token.endswith('"') else token
            content_words.append(text)
        return self._pipeline.process(" ".join(content_words))

    def _extract_raw_query_words(self, query: str) -> list[str]:
        tokens = _QUERY_TOKEN_PATTERN.findall(query.strip())
        words = []
        for token in tokens:
            if token.upper() in ("AND", "OR", "NOT"):
                continue
            text = token[1:-1] if token.startswith('"') and token.endswith('"') else token
            words.extend(re.findall(r"\w+", text))
        return words

    def _make_snippet(self, raw_text: str, highlight_words: list[str], window: int = 12) -> str:
        words = raw_text.split()
        lower_words = [w.lower() for w in words]
        query_words_lower = [w.lower() for w in highlight_words]

        match_index = None
        for i, word in enumerate(lower_words):
            if any(qw in word for qw in query_words_lower):
                match_index = i
                break

        if match_index is None:
            snippet_words = words[: window * 2]
        else:
            start = max(0, match_index - window)
            end = min(len(words), match_index + window)
            snippet_words = words[start:end]

        snippet = " ".join(snippet_words)
        return snippet + ("..." if len(snippet_words) < len(words) else "")

    def _execute_query(self, query: str) -> set[int]:
        tokens = _QUERY_TOKEN_PATTERN.findall(query.strip())
        if not tokens:
            return set()

        result: set[int] | None = None
        pending_op = "AND"

        for token in tokens:
            upper = token.upper()
            if upper in ("AND", "OR", "NOT"):
                pending_op = upper
                continue

            if token.startswith('"') and token.endswith('"') and len(token) > 1:
                operand = self._phrase_search.search(token[1:-1])
            else:
                operand = self._boolean_search.search_and([token])

            if result is None:
                result = operand
            elif pending_op == "AND":
                result &= operand
            elif pending_op == "OR":
                result |= operand
            elif pending_op == "NOT":
                result -= operand

            pending_op = "AND"

        return result or set()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m search_engine.cli.main <documents_folder>")
        sys.exit(1)

    engine = SearchEngineCLI()
    folder = sys.argv[1]

    print(f"Indexing documents in {folder} ...")
    count = engine.index_directory(folder)
    print(f"Indexed {count} documents ({engine.vocabulary_size} unique terms).\n")
    print('Query syntax: bare words = AND, "quoted phrase" = exact phrase, '
          'AND/OR/NOT supported. Type "exit" to quit.')

    while True:
        try:
            query = input("\nsearch> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if query.lower() in ("exit", "quit"):
            break
        if not query:
            continue

        results = engine.search(query)
        if not results:
            print("  No results found.")
        else:
            print(f"  {len(results)} result(s):")
            for doc_id, title, path in results:
                print(f"    [{doc_id}] {title}  ({path})")


if __name__ == "__main__":
    main()