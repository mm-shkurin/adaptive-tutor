import asyncio
from uuid import UUID

from usecase.document.errors import RateLimited, RateUnavailable

LIMIT = 5


class MemoryUploadRateLimit:
    def __init__(self, clock):
        self.clock = clock
        self.fail_reads = False
        self._counts: dict[str, int] = {}
        self._lock = asyncio.Lock()

    async def try_accept(self, owner_id: UUID) -> None:
        if self.fail_reads:
            raise RateUnavailable()
        async with self._lock:
            key = self._key(owner_id)
            count = self._counts.get(key, 0)
            if count >= LIMIT:
                raise RateLimited()
            self._counts[key] = count + 1

    async def release(self, owner_id: UUID) -> None:
        async with self._lock:
            key = self._key(owner_id)
            count = self._counts.get(key, 0)
            if count > 0:
                self._counts[key] = count - 1

    def _key(self, owner_id: UUID) -> str:
        return f"{owner_id}:{self.clock.now().strftime('%Y%m%d%H%M')}"
