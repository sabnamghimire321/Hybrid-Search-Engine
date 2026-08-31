from search_engine.performance.profiler import (
    profile_and_return,
    profile_function,
    top_time_consumers,
)

def _slow_function(n: int) -> int:
    total = 0
    for i in range(n):
        total += i
    return total

def test_profile_function_returns_a_readable_report():
    report = profile_function(_slow_function, 10000)
    assert isinstance(report, str)
    assert "function calls" in report
    assert "_slow_function" in report

def test_profile_and_return_gives_back_actual_result():
    result, stats = profile_and_return(_slow_function, 100)
    assert result == sum(range(100))

def test_profile_and_return_gives_usable_stats_object():
    _, stats = profile_and_return(_slow_function, 1000)
    assert hasattr(stats, "stats")
    assert len(stats.stats) > 0

def test_top_time_consumers_returns_requested_count():
    _, stats = profile_and_return(_slow_function, 5000)
    top = top_time_consumers(stats, n=3)
    assert len(top) <= 3
    for label, cumulative_time, call_count in top:
        assert isinstance(label, str)
        assert cumulative_time >= 0
        assert call_count >= 0

def test_top_time_consumers_sorted_by_cumulative_time_descending():
    def nested_calls():
        for _ in range(100):
            _slow_function(50)

    _, stats = profile_and_return(nested_calls)
    top = top_time_consumers(stats, n=10)

    cumulative_times = [entry[1] for entry in top]
    assert cumulative_times == sorted(cumulative_times, reverse=True)

def test_profiling_a_real_indexing_benchmark_surfaces_add_document():
    from search_engine.performance.benchmarks import benchmark_indexing

    _, stats = profile_and_return(benchmark_indexing, num_docs=200, doc_length=20)
    top = top_time_consumers(stats, n=50)
    labels = [entry[0] for entry in top]

    assert any("add_document" in label for label in labels)