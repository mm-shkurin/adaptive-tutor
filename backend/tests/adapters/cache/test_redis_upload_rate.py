from datetime import datetime, timezone
from uuid import uuid4

import pytest
from redis.exceptions import RedisError

from adapters.cache.redis_upload_rate import LIMIT, RedisUploadRateLimit
from usecase.document.errors import RateLimited, RateUnavailable


class _Clock:
    def __init__(self, moment: datetime):
        self.moment = moment

    def now(self):
        return self.moment


class _Redis:
    def __init__(self):
        self.values: dict[str, int] = {}
        self.fail = False

    async def eval(self, _script, _numkeys, key, limit, _ttl):
        if self.fail:
            raise RedisError("down")
        count = self.values.get(key, 0) + 1
        if count > int(limit):
            return 0
        self.values[key] = count
        return 1

    async def decr(self, key):
        self.values[key] = self.values.get(key, 0) - 1


@pytest.mark.asyncio
async def test_redis_rate_allows_five_then_refuses():
    redis = _Redis()
    rates = RedisUploadRateLimit(redis, _Clock(datetime(2024, 5, 6, 7, 8, 9, tzinfo=timezone.utc)))
    owner = uuid4()
    for _ in range(LIMIT):
        await rates.try_accept(owner)
    with pytest.raises(RateLimited):
        await rates.try_accept(owner)


@pytest.mark.asyncio
async def test_redis_rate_unavailable_when_store_errors():
    redis = _Redis()
    redis.fail = True
    rates = RedisUploadRateLimit(redis, _Clock(datetime(2024, 5, 6, 7, 8, 9, tzinfo=timezone.utc)))
    with pytest.raises(RateUnavailable):
        await rates.try_accept(uuid4())
