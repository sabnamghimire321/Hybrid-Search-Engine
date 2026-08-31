import pytest

from search_engine.crawler.url_frontier import UrlFrontier

def test_add_new_url_returns_true():
    frontier = UrlFrontier()
    assert frontier.add("http://example.com/a") is True

def test_add_duplicate_url_returns_false():
    frontier = UrlFrontier()
    frontier.add("http://example.com/a")
    assert frontier.add("http://example.com/a") is False

def test_next_returns_urls_in_fifo_bfs_order():
    frontier = UrlFrontier()
    frontier.add("http://example.com/a")
    frontier.add("http://example.com/b")
    frontier.add("http://example.com/c")

    assert frontier.next() == "http://example.com/a"
    assert frontier.next() == "http://example.com/b"
    assert frontier.next() == "http://example.com/c"

def test_duplicate_add_does_not_requeue():
    frontier = UrlFrontier()
    frontier.add("http://example.com/a")
    frontier.add("http://example.com/a")
    frontier.add("http://example.com/b")

    assert len(frontier) == 2
    assert frontier.next() == "http://example.com/a"
    assert frontier.next() == "http://example.com/b"

def test_next_on_empty_frontier_raises():
    frontier = UrlFrontier()
    with pytest.raises(IndexError):
        frontier.next()

def test_has_next_reflects_queue_state():
    frontier = UrlFrontier()
    assert frontier.has_next() is False
    frontier.add("http://example.com/a")
    assert frontier.has_next() is True
    frontier.next()
    assert frontier.has_next() is False

def test_has_seen_tracks_all_ever_added():
    frontier = UrlFrontier()
    frontier.add("http://example.com/a")
    frontier.next()

    assert frontier.has_seen("http://example.com/a") is True
    assert frontier.has_seen("http://example.com/never-added") is False

def test_seen_count_includes_visited_and_still_queued():
    frontier = UrlFrontier()
    frontier.add("http://example.com/a")
    frontier.add("http://example.com/b")
    frontier.next()

    assert frontier.seen_count == 2
    assert len(frontier) == 1