from search_engine.core.preprocessing.stemmer import PorterStemmer


def test_step1a_plurals():
    s = PorterStemmer()
    assert s.stem("caresses") == "caress"
    assert s.stem("ponies") == "poni"
    assert s.stem("cats") == "cat"


def test_step1b_eed_requires_positive_measure():
    s = PorterStemmer()
    assert s.stem("agreed") == "agre"
    assert s.stem("feed") == "feed"


def test_step1b_ed_ing_require_vowel_in_stem():
    s = PorterStemmer()
    assert s.stem("plastered") == "plaster"
    assert s.stem("motoring") == "motor"
    assert s.stem("sing") == "sing"


def test_double_consonant_and_cvc_cleanup():
    s = PorterStemmer()
    assert s.stem("hopping") == "hop"
    assert s.stem("tanned") == "tan"
    assert s.stem("hissing") == "hiss"
    assert s.stem("sized") == "size"


def test_maximal_munch_does_not_overstem():
    s = PorterStemmer()
    assert s.stem("argument") == "argument"
    assert s.stem("government") == "govern"


def test_step2_and_step3_suffix_chains():
    s = PorterStemmer()
    assert s.stem("relational") == "relat"
    assert s.stem("conditional") == "condit"
    assert s.stem("triplicate") == "triplic"
    assert s.stem("electriciti") == "electr"


def test_step4_common_endings():
    s = PorterStemmer()
    assert s.stem("adoption") == "adopt"
    assert s.stem("activate") == "activ"
    assert s.stem("effective") == "effect"


def test_short_words_are_left_alone():
    s = PorterStemmer()
    assert s.stem("is") == "is"
    assert s.stem("a") == "a"


def test_stem_all_preserves_order():
    s = PorterStemmer()
    result = s.stem_all(["running", "flies", "happiness"])
    assert result == ["run", "fli", "happi"]