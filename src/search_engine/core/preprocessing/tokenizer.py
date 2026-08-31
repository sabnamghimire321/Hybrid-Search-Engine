import re

class Tokenizer:
    _TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]+")

    def tokenize(self, text: str) -> list[str]:
        return [match.group().lower() for match in self._TOKEN_PATTERN.finditer(text)]