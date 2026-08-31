import cProfile
import io
import pstats
from typing import Any, Callable

def profile_function(func: Callable, *args: Any, top_n: int = 20, **kwargs: Any) -> str:
    profiler = cProfile.Profile()
    profiler.enable()
    func(*args, **kwargs)
    profiler.disable()

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
    stats.print_stats(top_n)
    return stream.getvalue()

def profile_and_return(func: Callable, *args: Any, **kwargs: Any) -> tuple[Any, pstats.Stats]:
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()

    stats = pstats.Stats(profiler)
    return result, stats

def top_time_consumers(stats: pstats.Stats, n: int = 10) -> list[tuple[str, float, int]]:
    stats.sort_stats("cumulative")
    entries = []

    for func_key, (call_count, _num_calls, _total_time, cumulative_time, _callers) in stats.stats.items():
        filename, line_number, func_name = func_key
        label = f"{func_name} ({filename.split('/')[-1]}:{line_number})"
        entries.append((label, cumulative_time, call_count))

    entries.sort(key=lambda entry: entry[1], reverse=True)
    return entries[:n]