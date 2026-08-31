from search_engine.api.analytics import QueryHistoryStore

def test_record_and_total_queries():
    store = QueryHistoryStore()
    store.record("key-a", "python search", 5, timestamp=100.0)
    store.record("key-a", "java tutorial", 2, timestamp=101.0)

    assert store.total_queries() == 2
    assert store.total_queries("key-a") == 2
    assert store.total_queries("key-b") == 0

def test_history_for_returns_newest_first():
    store = QueryHistoryStore()
    store.record("key-a", "first query", 1, timestamp=100.0)
    store.record("key-a", "second query", 2, timestamp=200.0)
    store.record("key-a", "third query", 3, timestamp=300.0)

    history = store.history_for("key-a")
    queries_in_order = [h["query"] for h in history]
    assert queries_in_order == ["third query", "second query", "first query"]

def test_history_for_respects_limit():
    store = QueryHistoryStore()
    for i in range(10):
        store.record("key-a", f"query {i}", 1, timestamp=float(i))

    history = store.history_for("key-a", limit=3)
    assert len(history) == 3

def test_history_isolated_per_api_key():
    store = QueryHistoryStore()
    store.record("key-a", "query from a", 1, timestamp=100.0)
    store.record("key-b", "query from b", 1, timestamp=100.0)

    history_a = store.history_for("key-a")
    assert len(history_a) == 1
    assert history_a[0]["query"] == "query from a"

def test_top_queries_ranks_by_frequency():
    store = QueryHistoryStore()
    store.record("key-a", "popular", 5, timestamp=100.0)
    store.record("key-b", "popular", 3, timestamp=101.0)
    store.record("key-a", "popular", 4, timestamp=102.0)
    store.record("key-a", "rare", 1, timestamp=103.0)

    top = store.top_queries(limit=5)
    assert top[0]["query"] == "popular"
    assert top[0]["count"] == 3
    assert top[1]["query"] == "rare"
    assert top[1]["count"] == 1

def test_queries_per_user():
    store = QueryHistoryStore()
    store.record("key-a", "q1", 1, timestamp=100.0)
    store.record("key-a", "q2", 1, timestamp=101.0)
    store.record("key-b", "q3", 1, timestamp=102.0)

    per_user = store.queries_per_user()
    per_user_dict = {row["api_key"]: row["count"] for row in per_user}
    assert per_user_dict == {"key-a": 2, "key-b": 1}

def test_average_result_count():
    store = QueryHistoryStore()
    store.record("key-a", "q1", 10, timestamp=100.0)
    store.record("key-a", "q2", 20, timestamp=101.0)

    assert store.average_result_count() == 15.0

def test_average_result_count_empty_history_returns_zero():
    store = QueryHistoryStore()
    assert store.average_result_count() == 0.0

def test_default_timestamp_uses_current_time():
    store = QueryHistoryStore()
    store.record("key-a", "query", 1)
    assert store.total_queries("key-a") == 1