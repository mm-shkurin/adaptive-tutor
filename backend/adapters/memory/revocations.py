import hashlib
from datetime import datetime


class MemoryRevocations:
    def __init__(self):
        self._until: dict[str, datetime] = {}

    async def revoke(self, token: str, expires_at: datetime) -> None:
        self._until[_fingerprint(token)] = expires_at

    async def is_revoked(self, token: str) -> bool:
        return _fingerprint(token) in self._until


def _fingerprint(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
