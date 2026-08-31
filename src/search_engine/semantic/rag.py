import os
import re
from typing import Callable, Protocol

class QueryRewriter:
    _DEFAULT_SYNONYMS: dict[str, list[str]] = {
        "fast": ["quick", "rapid", "speedy"],
        "error": ["bug", "exception", "issue"],
        "function": ["method", "procedure"],
        "big": ["large", "huge"],
        "small": ["tiny", "little"],
        "start": ["begin", "launch"],
        "search": ["find", "lookup", "query"],
    }

    def __init__(self, synonyms: dict[str, list[str]] | None = None) -> None:
        self._synonyms = synonyms if synonyms is not None else dict(self._DEFAULT_SYNONYMS)

    def expand(self, query: str) -> list[str]:
        words = query.lower().split()
        variants = [query]

        for i, word in enumerate(words):
            if word in self._synonyms:
                for synonym in self._synonyms[word]:
                    variant_words = words[:i] + [synonym] + words[i + 1 :]
                    variants.append(" ".join(variant_words))

        return variants

class AnswerGenerator(Protocol):
    def generate(self, query: str, retrieved_snippets: list[str]) -> str: ...

class ExtractiveAnswerGenerator:
    def generate(self, query: str, retrieved_snippets: list[str]) -> str:
        if not retrieved_snippets:
            return "No relevant information found."

        query_words = set(query.lower().split())
        best_sentence = ""
        best_overlap = -1

        for snippet in retrieved_snippets:
            for sentence in self._split_sentences(snippet):
                sentence_words = set(sentence.lower().split())
                overlap = len(query_words & sentence_words)
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_sentence = sentence.strip()

        return best_sentence if best_sentence else retrieved_snippets[0][:200]

    def _split_sentences(self, text: str) -> list[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s for s in sentences if s.strip()]

class LLMAnswerGenerator:
    def __init__(self, model: str = "claude-sonnet-4-6") -> None:
        try:
            import anthropic

            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise RuntimeError("ANTHROPIC_API_KEY environment variable not set")

            self._client = anthropic.Anthropic(api_key=api_key)
            self._model = model
        except Exception as e:
            raise ImportError(
                "LLMAnswerGenerator could not be initialized (missing 'anthropic' "
                "package, missing ANTHROPIC_API_KEY environment variable, or another "
                "setup issue). This is intentionally NOT required for this project to "
                "function or be tested -- use ExtractiveAnswerGenerator instead for a "
                f"dependency-free, no-API-key answer generator. Original error: {e}"
            ) from e

    def generate(self, query: str, retrieved_snippets: list[str]) -> str:
        context = "\n\n".join(
            f"[Document {i + 1}]: {snippet}" for i, snippet in enumerate(retrieved_snippets)
        )
        prompt = (
            "Answer the following question using ONLY the provided context. "
            "If the context doesn't contain enough information, say so.\n\n"
            f"Context:\n{context}\n\nQuestion: {query}"
        )
        response = self._client.messages.create(
            model=self._model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

class RAGPipeline:
    def __init__(
        self,
        retriever: Callable[[str], list[str]],
        answer_generator: AnswerGenerator,
        query_rewriter: QueryRewriter | None = None,
    ) -> None:
        self._retriever = retriever
        self._answer_generator = answer_generator
        self._query_rewriter = query_rewriter

    def answer(self, query: str) -> str:
        queries_to_try = [query]
        if self._query_rewriter is not None:
            queries_to_try = self._query_rewriter.expand(query)

        all_snippets: list[str] = []
        seen: set[str] = set()
        for q in queries_to_try:
            for snippet in self._retriever(q):
                if snippet not in seen:
                    seen.add(snippet)
                    all_snippets.append(snippet)

        return self._answer_generator.generate(query, all_snippets)