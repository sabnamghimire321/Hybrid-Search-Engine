import re

class PorterStemmer:

    _VOWELS = set("aeiou")

    def _is_consonant(self, word: str, i: int) -> bool:
        ch = word[i]
        if ch in self._VOWELS:
            return False
        if ch == "y":
            if i == 0:
                return True
            return not self._is_consonant(word, i - 1)
        return True

    def _measure(self, stem: str) -> int:
        """Counts VC (vowel-group -> consonant-group) transitions.
        A word's form is [C](VC)^m[V]; this returns m."""
        form = "".join("C" if self._is_consonant(stem, i) else "V" for i in range(len(stem)))
        form = re.sub(r"^C+", "", form)
        form = re.sub(r"V+$", "", form)
        return form.count("VC")

    def _contains_vowel(self, stem: str) -> bool:
        return any(not self._is_consonant(stem, i) for i in range(len(stem)))

    def _ends_double_consonant(self, stem: str) -> bool:
        if len(stem) < 2:
            return False
        return stem[-1] == stem[-2] and self._is_consonant(stem, len(stem) - 1)

    def _ends_cvc(self, stem: str) -> bool:
        """Stem ends consonant-vowel-consonant, where the final consonant
        is not w, x, or y (e.g. "hop", "wil" match; "how", "max" don't)."""
        if len(stem) < 3:
            return False
        idx = len(stem) - 1
        return (
            self._is_consonant(stem, idx - 2)
            and not self._is_consonant(stem, idx - 1)
            and self._is_consonant(stem, idx)
            and stem[-1] not in ("w", "x", "y")
        )

    def _apply_longest_suffix_rule(self, word: str, rules: list[tuple]) -> str:
        candidates = [r for r in rules if r[0] == "" or word.endswith(r[0])]
        if not candidates:
            return word

        suffix, replacement, condition = max(candidates, key=lambda r: len(r[0]))
        stem = word[: len(word) - len(suffix)] if suffix else word

        if condition is None or condition(stem):
            return stem + replacement
        return word

    def _step1a(self, word: str) -> str:
        rules = [("sses", "ss", None), ("ies", "i", None), ("ss", "ss", None), ("s", "", None)]
        return self._apply_longest_suffix_rule(word, rules)

    def _step1b(self, word: str) -> str:
        if word.endswith("eed"):
            stem = word[:-3]
            if self._measure(stem) > 0:
                return stem + "ee"
            return word

        for suffix in ("ing", "ed"):
            if word.endswith(suffix):
                stem = word[: -len(suffix)]
                if self._contains_vowel(stem):
                    return self._step1b_post_cleanup(stem)
                return word
        return word

    def _step1b_post_cleanup(self, stem: str) -> str:
        if stem.endswith(("at", "bl", "iz")):
            return stem + "e"
        if self._ends_double_consonant(stem) and stem[-1] not in ("l", "s", "z"):
            return stem[:-1]
        if self._measure(stem) == 1 and self._ends_cvc(stem):
            return stem + "e"
        return stem

    def _step1c(self, word: str) -> str:
        if word.endswith("y") and len(word) > 1 and self._contains_vowel(word[:-1]):
            return word[:-1] + "i"
        return word

    _STEP2_RULES = [
        ("ational", "ate", lambda s: True), ("tional", "tion", lambda s: True),
        ("enci", "ence", lambda s: True), ("anci", "ance", lambda s: True),
        ("izer", "ize", lambda s: True), ("abli", "able", lambda s: True),
        ("alli", "al", lambda s: True), ("entli", "ent", lambda s: True),
        ("eli", "e", lambda s: True), ("ousli", "ous", lambda s: True),
        ("ization", "ize", lambda s: True), ("ation", "ate", lambda s: True),
        ("ator", "ate", lambda s: True), ("alism", "al", lambda s: True),
        ("iveness", "ive", lambda s: True), ("fulness", "ful", lambda s: True),
        ("ousness", "ous", lambda s: True), ("aliti", "al", lambda s: True),
        ("iviti", "ive", lambda s: True), ("biliti", "ble", lambda s: True),
    ]

    def _step2(self, word: str) -> str:
        rules = [(suf, repl, lambda s: self._measure(s) > 0) for suf, repl, _ in self._STEP2_RULES]
        return self._apply_longest_suffix_rule(word, rules)

    _STEP3_SUFFIXES = [
        ("icate", "ic"), ("ative", ""), ("alize", "al"), ("iciti", "ic"),
        ("ical", "ic"), ("ful", ""), ("ness", ""),
    ]

    def _step3(self, word: str) -> str:
        rules = [(suf, repl, lambda s: self._measure(s) > 0) for suf, repl in self._STEP3_SUFFIXES]
        return self._apply_longest_suffix_rule(word, rules)

    _STEP4_SUFFIXES = [
        "al", "ance", "ence", "er", "ic", "able", "ible", "ant", "ement",
        "ment", "ent", "ou", "ism", "ate", "iti", "ous", "ive", "ize",
    ]

    def _step4(self, word: str) -> str:
        rules = [(suf, "", lambda s: self._measure(s) > 1) for suf in self._STEP4_SUFFIXES]
        rules.append(
            ("ion", "", lambda s: self._measure(s) > 1 and s.endswith(("s", "t")))
        )
        return self._apply_longest_suffix_rule(word, rules)

    def _step5a(self, word: str) -> str:
        if word.endswith("e"):
            stem = word[:-1]
            m = self._measure(stem)
            if m > 1:
                return stem
            if m == 1 and not self._ends_cvc(stem):
                return stem
        return word

    def _step5b(self, word: str) -> str:
        if (
            self._measure(word) > 1
            and self._ends_double_consonant(word)
            and word.endswith("l")
        ):
            return word[:-1]
        return word

    def stem(self, word: str) -> str:
        """Applies all Porter algorithm steps in sequence to a single word."""
        if len(word) <= 2:
            return word
        w = word.lower()
        w = self._step1a(w)
        w = self._step1b(w)
        w = self._step1c(w)
        w = self._step2(w)
        w = self._step3(w)
        w = self._step4(w)
        w = self._step5a(w)
        w = self._step5b(w)
        return w

    def stem_all(self, tokens: list[str]) -> list[str]:
        return [self.stem(t) for t in tokens]