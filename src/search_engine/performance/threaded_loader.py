import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

def _read_one_file(path: Path, simulated_io_delay: float = 0.0) -> tuple[str, str]:
    if simulated_io_delay > 0:
        time.sleep(simulated_io_delay)
    return str(path), path.read_text(encoding="utf-8", errors="replace")

def load_documents_threaded(
    paths: list[Path], num_workers: int = 4, simulated_io_delay: float = 0.0
) -> dict[str, str]:
    if not paths:
        return {}

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        results = list(
            executor.map(lambda p: _read_one_file(p, simulated_io_delay), paths)
        )

    return dict(results)

def load_documents_sequential(paths: list[Path], simulated_io_delay: float = 0.0) -> dict[str, str]:
    """Baseline for comparison: reads files one at a time, no threading."""
    return dict(_read_one_file(path, simulated_io_delay) for path in paths)