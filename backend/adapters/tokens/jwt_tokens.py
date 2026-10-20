from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt


@dataclass(frozen=True)
class TokenClaims:
    user_id: UUID
    expires_at: datetime
    kind: str


class JwtTokens:
    def __init__(self, access_secret: str, refresh_secret: str, access_ttl: timedelta, refresh_ttl: timedelta):
        self.access_secret = access_secret
        self.refresh_secret = refresh_secret
        self.access_ttl = access_ttl
        self.refresh_ttl = refresh_ttl

    def issue(self, user_id: UUID):
        from usecase.account.sign_in import TokenPair

        return TokenPair(self.issue_access(user_id), self._encode(user_id, "refresh"))

    def issue_access(self, user_id: UUID) -> str:
        return self._encode(user_id, "access")

    def read(self, token: str, kind: str) -> TokenClaims | None:
        secret = self.access_secret if kind == "access" else self.refresh_secret
        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])
        except jwt.PyJWTError:
            return None
        if payload.get("type") != kind or not payload.get("sub"):
            return None
        try:
            user_id = UUID(payload["sub"])
        except ValueError:
            return None
        expires_at = datetime.fromtimestamp(payload["exp"], timezone.utc)
        return TokenClaims(user_id, expires_at, kind)

    def _encode(self, user_id: UUID, kind: str) -> str:
        now = datetime.now(timezone.utc)
        ttl = self.access_ttl if kind == "access" else self.refresh_ttl
        secret = self.access_secret if kind == "access" else self.refresh_secret
        payload = {
            "sub": str(user_id),
            "type": kind,
            "jti": str(uuid4()),
            "iat": int(now.timestamp()),
            "exp": int((now + ttl).timestamp()),
        }
        return jwt.encode(payload, secret, algorithm="HS256")
