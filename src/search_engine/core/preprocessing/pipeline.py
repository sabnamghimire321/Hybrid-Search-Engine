from search_engine.core.preprocessing.stemmer import PorterStemmer
from search_engine.core.preprocessing.stopwords import StopwordFilter
from search_engine.core.preprocessing.tokenizer import Tokenizer


class Pipeline:
    def __init__(
        self,
        tokenizer: Tokenizer | None = None,
        stopword_filter: StopwordFilter | None = None,
        stemmer: PorterStemmer | None = None,
    ) -> None:
        self._tokenizer = tokenizer or Tokenizer()
        self._stopword_filter = stopword_filter or StopwordFilter()
        self._stemmer = stemmer or PorterStemmer()

    def process(self, text: str) -> list[str]:
        """Raw text -> final list of indexable tokens."""
        tokens = self._tokenizer.tokenize(text)
        tokens = self._stopword_filter.remove(tokens)
        tokens = self._stemmer.stem_all(tokens)
        return tokens