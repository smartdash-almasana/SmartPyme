from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Callable


class WorkerPool:
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def submit(self, fn: Callable, *args, **kwargs):
        return self.executor.submit(fn, *args, **kwargs)

    def shutdown(self, wait: bool = True) -> None:
        self.executor.shutdown(wait=wait)
