import pytest

from search_engine.semantic.rag import (
    ExtractiveAnswerGenerator,
    LLMAnswerGenerator,
    QueryRewriter,
    RAGPipeline,
)

def test_query_rewriter_expands_known_synonym():
    rewriter = QueryRewriter()
    variants = rewriter.expand("fast search")

    assert "fast search" in variants
    assert "quick search" in variants
    assert "rapid search" in variants

def test_query_rewriter_no_synonyms_returns_only_original():
    rewriter = QueryRewriter()
    variants = rewriter.expand("purple elephant dancing")
    assert variants == ["purple elephant dancing"]

def test_query_rewriter_custom_synonyms():
    rewriter = QueryRewriter(synonyms={"hello": ["hi", "hey"]})
    variants = rewriter.expand("hello world")
    assert set(variants) == {"hello world", "hi world", "hey world"}

def test_extractive_generator_picks_best_overlapping_sentence():
    generator = ExtractiveAnswerGenerator()
    snippets = [
        "Python is a popular programming language. It was created in 1991.",
        "The weather today is sunny and warm.",
    ]
    answer = generator.generate("when was python created", snippets)
    assert "1991" in answer

def test_extractive_generator_no_snippets_returns_fallback():
    generator = ExtractiveAnswerGenerator()
    assert generator.generate("anything", []) == "No relevant information found."

def test_extractive_generator_handles_multiple_sentences_per_snippet():
    generator = ExtractiveAnswerGenerator()
    snippets = ["First sentence here. Second sentence about python programming. Third one."]
    answer = generator.generate("python programming", snippets)
    assert "python programming" in answer.lower()

def test_llm_answer_generator_raises_helpful_error_when_unavailable():
    try:
        LLMAnswerGenerator()
        pytest.skip("anthropic package + API key are both available in this environment")
    except ImportError as exc_info:
        message = str(exc_info)
        assert "ExtractiveAnswerGenerator" in message

def test_rag_pipeline_without_rewriter_uses_original_query_only():
    calls = []

    def fake_retriever(query: str) -> list[str]:
        calls.append(query)
        return ["Python was created in 1991 by Guido van Rossum."]

    pipeline = RAGPipeline(fake_retriever, ExtractiveAnswerGenerator())
    answer = pipeline.answer("when was python created")

    assert calls == ["when was python created"]
    assert "1991" in answer

def test_rag_pipeline_with_rewriter_tries_all_variants():
    calls = []

    def fake_retriever(query: str) -> list[str]:
        calls.append(query)
        return [f"Result for: {query}"]

    rewriter = QueryRewriter(synonyms={"fast": ["quick"]})
    pipeline = RAGPipeline(fake_retriever, ExtractiveAnswerGenerator(), query_rewriter=rewriter)
    pipeline.answer("fast search")

    assert "fast search" in calls
    assert "quick search" in calls

def test_rag_pipeline_deduplicates_snippets_across_query_variants():
    def fake_retriever(query: str) -> list[str]:
        return ["The same shared snippet appears here regardless of query."]

    rewriter = QueryRewriter(synonyms={"fast": ["quick"]})

    seen_snippets = []

    class RecordingGenerator:
        def generate(self, query, retrieved_snippets):
            seen_snippets.extend(retrieved_snippets)
            return "dummy answer"

    pipeline = RAGPipeline(fake_retriever, RecordingGenerator(), query_rewriter=rewriter)
    pipeline.answer("fast search")

    assert seen_snippets.count("The same shared snippet appears here regardless of query.") == 1