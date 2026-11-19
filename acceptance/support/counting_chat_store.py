from datetime import datetime
from uuid import UUID

from domain.chat.chat import Chat
from usecase.chat.send_message import Attempt


class CountingChatStore:
    def __init__(self, inner):
        self._inner = inner
        self.reads = 0

    def reset_reads(self) -> None:
        self.reads = 0

    async def add(self, owner_id: UUID, chat: Chat, created_at: datetime) -> None:
        await self._inner.add(owner_id, chat, created_at)

    async def list_for(self, owner_id: UUID) -> tuple[Chat, ...]:
        self.reads += 1
        return await self._inner.list_for(owner_id)

    async def get(self, owner_id: UUID, chat_id: UUID) -> Chat | None:
        self.reads += 1
        return await self._inner.get(owner_id, chat_id)

    async def newest_for_document(self, owner_id: UUID, document_id: UUID) -> Chat | None:
        self.reads += 1
        return await self._inner.newest_for_document(owner_id, document_id)

    async def save(self, owner_id: UUID, chat: Chat) -> None:
        await self._inner.save(owner_id, chat)

    async def find_attempt(self, owner_id: UUID, chat_id: UUID, attempt_key: str) -> Attempt | None:
        self.reads += 1
        return await self._inner.find_attempt(owner_id, chat_id, attempt_key)

    async def save_attempt(
        self, owner_id: UUID, chat_id: UUID, attempt_key: str, attempt: Attempt
    ) -> None:
        await self._inner.save_attempt(owner_id, chat_id, attempt_key, attempt)

    async def with_attempt(self, owner_id: UUID, chat_id: UUID, attempt_key: str, build):
        return await self._inner.with_attempt(owner_id, chat_id, attempt_key, build)

    async def commit_attempt(
        self, owner_id: UUID, chat_id: UUID, attempt_key: str, attempt: Attempt
    ) -> Attempt:
        return await self._inner.commit_attempt(owner_id, chat_id, attempt_key, attempt)

    def arm_thread_interleave(self, latch) -> None:
        self._inner.arm_thread_interleave(latch)

    def arm_attempt_interleave(self, latch) -> None:
        self._inner.arm_attempt_interleave(latch)
