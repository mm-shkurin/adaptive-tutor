import asyncio


class VectorLatch:
    def __init__(self, waiters: int = 2):
        self._waiters = waiters
        self._arrived = 0
        self._release = asyncio.Event()
        self._lock = asyncio.Lock()

    async def after_read(self) -> None:
        async with self._lock:
            self._arrived += 1
            if self._arrived >= self._waiters:
                self._release.set()
        await self._release.wait()
