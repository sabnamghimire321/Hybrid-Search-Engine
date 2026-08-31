import pytest
from search_engine.datastructures.lru_cache import LRUCache

def test_put_and_get():
    cache = LRUCache(capacity=2)
    cache.put("a", 1)
    assert cache.get("a") == 1

def test_get_missing_key_raises():
    cache = LRUCache(capacity=2)
    with pytest.raises(KeyError):
        cache.get("missing")

def test_get_or_default():
    cache = LRUCache(capacity=2)
    assert cache.get_or_default("missing", "fallback") == "fallback"

def test_eviction_removes_least_recently_used():
    cache = LRUCache(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3) 
    assert "a" not in cache
    assert cache.get("b") == 2
    assert cache.get("c") == 3


def test_get_marks_key_as_recently_used():
    cache = LRUCache(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")  
    cache.put("c", 3)  
    assert "a" in cache
    assert "b" not in cache
    assert cache.get("c") == 3

def test_put_existing_key_updates_value_and_recency():
    cache = LRUCache(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("a", 100)  
    cache.put("c", 3)  
    assert cache.get("a") == 100
    assert "b" not in cache

def test_capacity_one():
    cache = LRUCache(capacity=1)
    cache.put("a", 1)
    cache.put("b", 2)  
    assert "a" not in cache
    assert cache.get("b") == 2

def test_invalid_capacity_raises():
    with pytest.raises(ValueError):
        LRUCache(capacity=0)
    with pytest.raises(ValueError):
        LRUCache(capacity=-5)

def test_len_and_contains():
    cache = LRUCache(capacity=3)
    cache.put("a", 1)
    cache.put("b", 2)
    assert len(cache) == 2
    assert "a" in cache
    assert "z" not in cache

def test_repeated_access_pattern_never_corrupts_the_list():
    cache = LRUCache(capacity=3)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    cache.get("a")
    cache.get("b")
    cache.put("d", 4)  
    assert "c" not in cache
    cache.get("a")
    cache.put("e", 5)  
    assert "b" not in cache
    assert set(["a", "d", "e"]) == {k for k in ("a", "b", "c", "d", "e") if k in cache}