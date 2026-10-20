from datetime import datetime, timezone
from uuid import UUID

from domain.account.account import Account
from domain.account.name import decide_name
from domain.account.photo import photo_type
from usecase.account.errors import Unauthorized
from usecase.account.ports import AccountStore


class ProfileService:
    def __init__(self, accounts: AccountStore, public_base_url: str):
        self.accounts = accounts
        self.public_base_url = public_base_url.rstrip("/")

    def view(self, account: Account) -> dict:
        return {
            "id": str(account.id),
            "name": account.shown_name(),
            "email": account.email,
            "avatar_url": self._url(account.avatar_key),
            "created_at": _iso(account.created_at),
        }

    async def rename(self, account: Account, name: str) -> dict:
        updated = await self.accounts.save(account.with_profile_name(decide_name(name)))
        return self.view(await self._present(updated))

    async def replace_photo(self, account: Account, body: bytes) -> dict:
        content_type = photo_type(body)
        updated = await self.accounts.set_avatar(account.id, body, content_type)
        return self.view(await self._present(updated))

    async def remove_photo(self, account: Account) -> dict:
        updated = await self.accounts.clear_avatar(account.id)
        return self.view(await self._present(updated))

    async def remove_account(self, account: Account) -> None:
        await self.accounts.delete(account.id)

    def _url(self, key: UUID | None) -> str | None:
        if key is None:
            return None
        return f"{self.public_base_url}/api/v1/media/avatars/{key}"

    async def _present(self, account: Account | None) -> Account:
        if account is None:
            raise Unauthorized()
        return account


def _iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
