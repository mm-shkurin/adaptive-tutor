from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, IntegrityError, InterfaceError, OperationalError

from adapters.persistence.tables import AccountRow, AvatarRow
from domain.account.identity import ProviderIdentity
from usecase.account.errors import StoreUnavailable


class PostgresAccountStore:
    def __init__(self, sessions):
        self._sessions = sessions

    async def get(self, user_id: UUID):
        async def work(session):
            row = await session.get(AccountRow, user_id)
            return None if row is None else row.to_domain()

        return await self._run(work)

    async def get_or_create(self, identity: ProviderIdentity, created_at: datetime):
        try:
            return await self._run(lambda session: self._claim(session, identity, created_at))
        except IntegrityError:
            return await self._run(lambda session: self._reread(session, identity))

    async def save(self, account):
        async def work(session):
            row = await session.get(AccountRow, account.id)
            if row is None:
                return None
            row.apply(account)
            return row.to_domain()

        return await self._run(work)

    async def delete(self, user_id: UUID) -> None:
        async def work(session):
            row = await session.get(AccountRow, user_id)
            if row is None:
                return None
            if row.avatar_key is not None:
                avatar = await session.get(AvatarRow, row.avatar_key)
                if avatar is not None:
                    await session.delete(avatar)
            await session.delete(row)
            return None

        await self._run(work)

    async def set_avatar(self, user_id: UUID, body: bytes, content_type: str):
        async def work(session):
            row = await session.get(AccountRow, user_id)
            if row is None:
                return None
            key = uuid4()
            session.add(AvatarRow(key=key, owner_id=user_id, content_type=content_type, body=body))
            if row.avatar_key is not None:
                previous = await session.get(AvatarRow, row.avatar_key)
                if previous is not None:
                    await session.delete(previous)
            row.avatar_key = key
            return row.to_domain()

        return await self._run(work)

    async def clear_avatar(self, user_id: UUID):
        async def work(session):
            row = await session.get(AccountRow, user_id)
            if row is None:
                return None
            if row.avatar_key is not None:
                avatar = await session.get(AvatarRow, row.avatar_key)
                if avatar is not None:
                    await session.delete(avatar)
            row.avatar_key = None
            return row.to_domain()

        return await self._run(work)

    async def read_avatar(self, key: UUID):
        async def work(session):
            row = await session.get(AvatarRow, key)
            if row is None:
                return None
            return bytes(row.body), row.content_type

        return await self._run(work)

    async def _claim(self, session, identity: ProviderIdentity, created_at: datetime):
        found = await session.scalar(select(AccountRow).where(AccountRow.yandex_subject == identity.subject))
        if found is not None:
            found.email = identity.email
            found.provider_name = identity.name
            return found.to_domain()
        row = AccountRow(
            id=uuid4(),
            yandex_subject=identity.subject,
            email=identity.email,
            provider_name=identity.name,
            created_at=created_at,
        )
        session.add(row)
        await session.flush()
        return row.to_domain()

    async def _reread(self, session, identity: ProviderIdentity):
        found = await session.scalar(select(AccountRow).where(AccountRow.yandex_subject == identity.subject))
        if found is None:
            raise StoreUnavailable()
        found.email = identity.email
        found.provider_name = identity.name
        return found.to_domain()

    async def _run(self, work):
        try:
            async with self._sessions() as session:
                async with session.begin():
                    return await work(session)
        except IntegrityError:
            raise
        except (OperationalError, InterfaceError, DBAPIError) as error:
            raise StoreUnavailable() from error
