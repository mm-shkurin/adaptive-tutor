import asyncio
from datetime import datetime
from uuid import UUID, uuid4

from domain.account.account import Account
from domain.account.identity import ProviderIdentity
from usecase.account.errors import StoreUnavailable


class MemoryAccountStore:
    def __init__(self):
        self._rows: dict[UUID, Account] = {}
        self._by_subject: dict[str, UUID] = {}
        self._avatars: dict[UUID, tuple[bytes, str]] = {}
        self._lock = asyncio.Lock()
        self.dead = False
        self.live = 0

    def count(self) -> int:
        return len(self._rows)

    def avatar_count(self) -> int:
        return len(self._avatars)

    async def get(self, user_id: UUID) -> Account | None:
        async def action():
            return self._rows.get(user_id)

        return await self._guard(action)

    async def get_or_create(self, identity: ProviderIdentity, created_at: datetime) -> Account:
        async def action():
            async with self._lock:
                return self._claim(identity, created_at)

        return await self._guard(action)

    async def save(self, account: Account) -> Account | None:
        async def action():
            if account.id not in self._rows:
                return None
            self._rows[account.id] = account
            self._by_subject[account.yandex_subject] = account.id
            return account

        return await self._guard(action)

    async def delete(self, user_id: UUID) -> None:
        async def action():
            account = self._rows.pop(user_id, None)
            if account is None:
                return None
            self._by_subject.pop(account.yandex_subject, None)
            if account.avatar_key is not None:
                self._avatars.pop(account.avatar_key, None)
            return None

        await self._guard(action)

    async def set_avatar(self, user_id: UUID, body: bytes, content_type: str) -> Account | None:
        async def action():
            account = self._rows.get(user_id)
            if account is None:
                return None
            key = uuid4()
            self._avatars[key] = (body, content_type)
            if account.avatar_key is not None:
                self._avatars.pop(account.avatar_key, None)
            updated = account.with_avatar(key)
            self._rows[user_id] = updated
            return updated

        return await self._guard(action)

    async def clear_avatar(self, user_id: UUID) -> Account | None:
        async def action():
            account = self._rows.get(user_id)
            if account is None:
                return None
            if account.avatar_key is not None:
                self._avatars.pop(account.avatar_key, None)
            updated = account.with_avatar(None)
            self._rows[user_id] = updated
            return updated

        return await self._guard(action)

    async def read_avatar(self, key: UUID) -> tuple[bytes, str] | None:
        async def action():
            return self._avatars.get(key)

        return await self._guard(action)

    def _claim(self, identity: ProviderIdentity, created_at: datetime) -> Account:
        existing_id = self._by_subject.get(identity.subject)
        if existing_id is not None:
            updated = self._rows[existing_id].with_provider(identity)
            self._rows[existing_id] = updated
            return updated
        account = Account.open(identity, created_at)
        self._rows[account.id] = account
        self._by_subject[account.yandex_subject] = account.id
        return account

    async def _guard(self, action):
        self.live += 1
        try:
            if self.dead:
                raise StoreUnavailable()
            return await action()
        finally:
            self.live -= 1
