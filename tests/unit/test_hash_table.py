import pytest

from search_engine.datastructures.hash_table import HashTable


def test_put_and_get():
    table = HashTable()
    table.put("name", "Lara")
    assert table.get("name") == "Lara"


def test_get_missing_key_raises():
    table = HashTable()
    with pytest.raises(KeyError):
        table.get("nonexistent")


def test_get_or_default():
    table = HashTable()
    assert table.get_or_default("missing", "fallback") == "fallback"
    table.put("key", "value")
    assert table.get_or_default("key", "fallback") == "value"


def test_update_existing_key_does_not_grow_size():
    table = HashTable()
    table.put("x", 1)
    table.put("x", 2)
    assert table.get("x") == 2
    assert len(table) == 1


def test_delete_removes_key():
    table = HashTable()
    table.put("a", 1)
    table.delete("a")
    assert "a" not in table
    assert len(table) == 0


def test_delete_missing_key_raises():
    table = HashTable()
    with pytest.raises(KeyError):
        table.delete("nonexistent")


def test_contains_and_dunder_contains():
    table = HashTable()
    table.put("python", "search")
    assert table.contains("python") is True
    assert "python" in table
    assert "java" not in table


def test_forced_collisions_within_same_bucket_still_work():
    table = HashTable()
    table.put(0, "zero")
    table.put(8, "eight")
    table.put(16, "sixteen")

    assert table.get(0) == "zero"
    assert table.get(8) == "eight"
    assert table.get(16) == "sixteen"
    assert len(table) == 3


def test_resize_triggers_and_preserves_all_entries():
    table = HashTable()
    entries = {f"key{i}": i for i in range(50)}

    for k, v in entries.items():
        table.put(k, v)

    assert len(table) == 50
    for k, v in entries.items():
        assert table.get(k) == v


def test_dunder_setitem_getitem_delitem():
    table = HashTable()
    table["a"] = 1
    assert table["a"] == 1
    del table["a"]
    assert "a" not in table


def test_keys_values_items():
    table = HashTable()
    table.put("a", 1)
    table.put("b", 2)

    assert set(table.keys()) == {"a", "b"}
    assert set(table.values()) == {1, 2}
    assert set(table.items()) == {("a", 1), ("b", 2)}


def test_iteration_yields_keys():
    table = HashTable()
    table.put("x", 1)
    table.put("y", 2)
    assert set(table) == {"x", "y"}