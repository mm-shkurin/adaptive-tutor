from uuid import UUID

from redis.exceptions import RedisError

from usecase.document.errors import RateLimited, RateUnavailable

LIMIT = 5
_TTL_SECONDS = 120

_TRY = """
local n = redis.call('INCR', KEYS[1])
if n == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[2])
end
if n > tonumber(ARGV[1]) then
  redis.call('DECR', KEYS[1])
  return 0
end
return 1
"""


class RedisUploadRateLimit:
    def __init__(self, redis, clock):
        self.redis = redis
        self.clock = clock

    async def try_accept(self, owner_id: UUID) -> None:
        try:
            allowed = await self.redis.eval(_TRY, 1, self._key(owner_id), str(LIMIT), str(_TTL_SECONDS))
        except RedisError as error:
            raise RateUnavailable() from error
        if int(allowed) != 1:
            raise RateLimited()

    async def release(self, owner_id: UUID) -> None:
        try:
            await self.redis.decr(self._key(owner_id))
        except RedisError:
            return

    def _key(self, owner_id: UUID) -> str:
        stamp = self.clock.now().strftime("%Y%m%d%H%M")
        return f"doc_upload:{owner_id}:{stamp}"
