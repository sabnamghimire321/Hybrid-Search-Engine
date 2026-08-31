## Threading vs. multiprocessing: measured, not assumed

Directly compared threading against multiprocessing for the SAME
CPU-bound preprocessing workload (2,000 docs, full tokenize/stopword/
stem pipeline):

| Approach | Time | "Speedup" |
|---|---|---|
| Sequential | 1.885s | 1.00x |
| Threaded (4 threads) | 1.741s | 1.08x — essentially none |
| Multiprocessing (4 processes) | (see above) | 3.14x — real |

This confirms, with real numbers rather than textbook assertion, that
Python's GIL makes threading ineffective for CPU-bound work — only
one thread executes Python bytecode at a time regardless of thread
count, so 4 "parallel" threads doing CPU work run barely faster than 1.

Threading DOES help for a genuinely different problem: I/O-bound work,
where a thread waiting on disk/network I/O releases the GIL. Loading
16 files with a 20ms simulated I/O delay each: sequential ≈ 320ms,
threaded (4 workers) ≈ 80ms — a real ~4x improvement, because the wait
time (not CPU time) is what overlaps.

**Takeaway used throughout this project**: multiprocessing for CPU-bound
work (indexing/preprocessing), threading for I/O-bound work (file
loading, and in a real deployment, network calls), asyncio for
I/O-bound work when you want many more concurrent operations than
threads would comfortably support. Three different tools for two
different bottleneck types — not "parallelism = parallelism."