from search_engine.datastructures.trie import Trie

def test_insert_and_search_exact_word():
    trie = Trie()
    trie.insert("python")
    assert trie.search("python") is True
    assert trie.search("py") is False  
def test_search_word_never_inserted():
    trie = Trie()
    trie.insert("python")
    assert trie.search("java") is False


def test_starts_with_matches_prefixes():
    trie = Trie()
    trie.insert("search")
    assert trie.starts_with("sea") is True
    assert trie.starts_with("search") is True
    assert trie.starts_with("sear") is True
    assert trie.starts_with("java") is False


def test_shared_prefix_words_coexist():
    trie = Trie()
    for word in ["cat", "car", "card", "care"]:
        trie.insert(word)

    assert trie.search("cat") is True
    assert trie.search("car") is True
    assert trie.search("card") is True
    assert trie.search("care") is True
    assert trie.search("ca") is False  


def test_autocomplete_returns_all_matching_words():
    trie = Trie()
    for word in ["cat", "car", "card", "care", "dog"]:
        trie.insert(word)

    results = set(trie.autocomplete("car"))
    assert results == {"car", "card", "care"}


def test_autocomplete_no_matches_returns_empty():
    trie = Trie()
    trie.insert("python")
    assert trie.autocomplete("xyz") == []


def test_autocomplete_respects_limit():
    trie = Trie()
    for word in ["test1", "test2", "test3", "test4"]:
        trie.insert(word)

    results = trie.autocomplete("test", limit=2)
    assert len(results) == 2
    assert all(r.startswith("test") for r in results)


def test_delete_removes_word_but_keeps_shared_prefix_words():
    trie = Trie()
    trie.insert("card")
    trie.insert("care")

    assert trie.delete("card") is True
    assert trie.search("card") is False
    assert trie.search("care") is True


def test_delete_prunes_dead_branch_completely():
    trie = Trie()
    trie.insert("unique")

    trie.delete("unique")
    assert trie.starts_with("uniq") is False
    assert trie.search("unique") is False


def test_delete_nonexistent_word_returns_false():
    trie = Trie()
    trie.insert("python")
    assert trie.delete("java") is False
    assert len(trie) == 1


def test_len_and_contains():
    trie = Trie()
    trie.insert("a")
    trie.insert("b")
    trie.insert("a")  
    assert len(trie) == 2
    assert "a" in trie
    assert "c" not in trie


def test_insert_empty_string_is_noop():
    trie = Trie()
    trie.insert("")
    assert len(trie) == 0