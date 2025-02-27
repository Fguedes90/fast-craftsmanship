"""Progress tracking module with functional approach."""

import asyncio

from expression import Error, Ok, Result
from tqdm import tqdm


class ProgressTracker:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.total = 1
        self.completed = 0
        self.pbar = None

    def start(self):
        self.pbar = tqdm(
            total=self.total, desc="Downloading pages", unit="page", dynamic_ncols=True, miniters=1
        )

    def update(self, n=1):
        if self.pbar:
            self.pbar.update(n)

    def set_total(self, total):
        if self.pbar:
            self.pbar.total = total
            self.pbar.refresh()

    def close(self):
        if self.pbar:
            self.pbar.close()


async def update_progress(progress: ProgressTracker, n: int = 1) -> Result[None, Exception]:
    """Update progress with ROP."""
    try:
        async with progress.lock:
            progress.update(n)
        return Ok(None)
    except Exception as e:
        return Error(e)


async def increment_total(progress: ProgressTracker) -> Result[None, Exception]:
    """Increment total with ROP."""
    try:
        async with progress.lock:
            progress.total += 1
            progress.set_total(progress.total)
        return Ok(None)
    except Exception as e:
        return Error(e)
