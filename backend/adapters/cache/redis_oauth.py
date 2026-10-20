from datetime import datetime, timezone
from uuid import UUID

from redis.exceptions import RedisError


class RedisOAuthStore:
    def __init__(self, redis):
        self.redis = redis

    async def mint_state(self, state: str, provider: str, browser: str, expires_at: datetime) -> None:
        await self._mint(f"oauth:state:{state}", f"{provider}|{browser}|{_millis(expires_at)}", expires_at)

    async def take_state(self, state: str, provider: str, now: datetime) -> str | None:
        raw = await self._take(f"oauth:state:{state}", provider, _millis(now), match_browser=False)
        return raw

    async def mint_handoff(self, code: str, user_id: UUID, browser: str, expires_at: datetime) -> None:
        await self._mint(f"oauth:handoff:{code}", f"{user_id}|{browser}|{_millis(expires_at)}", expires_at)

    async def take_handoff(self, code: str, browser: str, now: datetime) -> UUID | None:
        raw = await self._take(f"oauth:handoff:{code}", browser, _millis(now), match_browser=True)
        if raw is None:
            return None
        return UUID(raw)

    async def _mint(self, key: str, value: str, expires_at: datetime) -> None:
        ttl = max(_millis(expires_at) - _millis(datetime.now(timezone.utc)), 1)
        await self.redis.set(key, value, px=ttl)

    async def _take(self, key: str, expected: str, now_ms: int, match_browser: bool) -> str | None:
        raw = await self.redis.eval(_TAKE, 1, key, expected, str(now_ms), "1" if match_browser else "0")
        if not raw:
            return None
        return raw.decode() if isinstance(raw, bytes) else raw


def _millis(moment: datetime) -> int:
    return int(moment.timestamp() * 1000)


# Deletes a spent or expired code. A browser mismatch leaves the code for its owner.
_TAKE = """
local raw = redis.call('GET', KEYS[1])
if not raw then return false end
local marker, browser, exp = string.match(raw, '([^|]+)|([^|]+)|([^|]+)')
if not marker then return false end
if tonumber(exp) <= tonumber(ARGV[2]) then
  redis.call('DEL', KEYS[1])
  return false
end
local expected_field = ARGV[3] == '1' and browser or marker
if expected_field ~= ARGV[1] then return false end
redis.call('DEL', KEYS[1])
return ARGV[3] == '1' and marker or browser
"""
