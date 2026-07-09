# utils/timing.py
"""
Simple timing helper for measuring request processing duration.
"""

import time


class Timer:
    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *exc_info) -> None:
        self.elapsed_ms = round((time.perf_counter() - self._start) * 1000, 2)