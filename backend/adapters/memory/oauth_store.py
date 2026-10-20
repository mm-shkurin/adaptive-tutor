import asyncio
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class _State:
    provider: str
    browser: str
    expires_at: datetime


@dataclass(frozen=True)
class _Handoff:
    user_id: UUID
    browser: str
    expires_at: datetime


class MemoryOAuthStore:
    """State and handoff codes. A code is spent once, and only by the browser that started."""

    def __init__(self):
        self._lock = asyncio.Lock()
        self._states: dict[str, _State] = {}
        self._handoffs: dict[str, _Handoff] = {}

    async def mint_state(self, state: str, provider: str, browser: str, expires_at: datetime) -> None:
        async with self._lock:
            self._states[state] = _State(provider, browser, expires_at)

    async def take_state(self, state: str, provider: str, now: datetime) -> str | None:
        async with self._lock:
            held = self._states.pop(state, None)
            if held is None or held.provider != provider or held.expires_at <= now:
                return None
            return held.browser

    async def mint_handoff(self, code: str, user_id: UUID, browser: str, expires_at: datetime) -> None:
        async with self._lock:
            self._handoffs[code] = _Handoff(user_id, browser, expires_at)

    async def take_handoff(self, code: str, browser: str, now: datetime) -> UUID | None:
        async with self._lock:
            held = self._handoffs.get(code)
            if held is None:
                return None
            if held.expires_at <= now:
                self._handoffs.pop(code, None)
                return None
            if held.browser != browser:
                return None
            self._handoffs.pop(code, None)
            return held.user_id
