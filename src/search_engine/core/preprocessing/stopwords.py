class StopwordFilter:
    _STOPWORDS: set[str] = {
        "a", "an", "the", "and", "or", "but", "if", "then", "else",
        "is", "are", "was", "were", "be", "been", "being",
        "in", "on", "at", "by", "for", "with", "about", "against",
        "to", "from", "of", "as", "into", "through", "during",
        "this", "that", "these", "those",
        "i", "you", "he", "she", "it", "we", "they",
        "me", "him", "her", "us", "them",
        "my", "your", "his", "its", "our", "their",
        "not", "no", "nor", "so", "too", "very",
        "can", "will", "just", "should", "now",
        "do", "does", "did", "doing",
        "have", "has", "had", "having",
        "there", "here", "when", "where", "why", "how",
        "all", "any", "both", "each", "few", "more", "most", "other",
        "some", "such", "only", "own", "same",
    }

    def remove(self, tokens: list[str]) -> list[str]:
        """Filters stopwords out of a token list, preserving order."""
        return [t for t in tokens if t not in self._STOPWORDS]

    def is_stopword(self, token: str) -> bool:
        return token in self._STOPWORDS