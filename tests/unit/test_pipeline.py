from search_engine.core.preprocessing.pipeline import Pipeline

def test_pipeline_full_flow():
    pipeline = Pipeline()
    result = pipeline.process("The Quick Brown Foxes are Jumping over Lazy Dogs!")
    assert result == ["quick", "brown", "fox", "jump", "over", "lazi", "dog"]

def test_pipeline_empty_text():
    assert Pipeline().process("") == []

def test_pipeline_all_stopwords_yields_empty():
    assert Pipeline().process("the a an is are") == []

def test_pipeline_accepts_injected_components():
    class UppercaseStemmer:
        def stem_all(self, tokens):
            return [t.upper() for t in tokens]

    pipeline = Pipeline(stemmer=UppercaseStemmer())
    result = pipeline.process("python search engine")
    assert result == ["PYTHON", "SEARCH", "ENGINE"]