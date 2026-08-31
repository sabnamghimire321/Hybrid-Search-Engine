import time

from search_engine.performance.threaded_loader import (
    load_documents_sequential,
    load_documents_threaded,
)

def _make_files(tmp_path, count: int) -> list:
    paths = []
    for i in range(count):
        p = tmp_path / f"doc{i}.txt"
        p.write_text(f"This is document number {i}")
        paths.append(p)
    return paths

def test_threaded_and_sequential_produce_identical_content(tmp_path):
    paths = _make_files(tmp_path, count=10)

    threaded_result = load_documents_threaded(paths, num_workers=4)
    sequential_result = load_documents_sequential(paths)

    assert threaded_result == sequential_result
    assert len(threaded_result) == 10

def test_empty_path_list_returns_empty_dict(tmp_path):
    assert load_documents_threaded([]) == {}
    assert load_documents_sequential([]) == {}

def test_content_is_read_correctly(tmp_path):
    paths = _make_files(tmp_path, count=3)
    result = load_documents_threaded(paths)

    for i, path in enumerate(paths):
        assert result[str(path)] == f"This is document number {i}"

def test_threading_genuinely_overlaps_io_wait_time(tmp_path):
    paths = _make_files(tmp_path, count=16)
    io_delay = 0.02

    start = time.perf_counter()
    load_documents_threaded(paths, num_workers=4, simulated_io_delay=io_delay)
    threaded_time = time.perf_counter() - start

    start = time.perf_counter()
    load_documents_sequential(paths, simulated_io_delay=io_delay)
    sequential_time = time.perf_counter() - start

    assert threaded_time < sequential_time * 0.7