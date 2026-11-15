import asyncio
from dataclasses import dataclass
from datetime import timedelta
from uuid import UUID

from domain.chat.chat import Chat, NotAskable
from domain.chat.learning import LearningMode, ListedModel, Question
from domain.chat.line import Line
from domain.chat.source import Source
from usecase.chat.errors import ChatNotFound, ReplyFailed
from usecase.chat.outgoing import Outgoing
from usecase.chat.ports import ChatStore, MaterialSearch, Tutor
from usecase.chat.reply_budget import CHAT_LATENCY, expired, remaining_seconds


@dataclass(frozen=True)
class ReplyError:
    code: str
    message: str

    @staticmethod
    def failed() -> "ReplyError":
        return ReplyError("reply_failed", "The model could not answer")

    def json(self) -> dict:
        return {"code": self.code, "message": self.message}


@dataclass(frozen=True)
class Attempt:
    chat_id: UUID
    lines: tuple[Line, ...]
    error: ReplyError | None = None


class SendMessage:
    def __init__(
        self,
        chats: ChatStore,
        search: MaterialSearch,
        tutor: Tutor,
        clock=None,
        latency: timedelta = CHAT_LATENCY,
    ):
        self.chats = chats
        self.search = search
        self.tutor = tutor
        self.clock = clock
        self.latency = latency

    async def send(
        self, owner_id: UUID, chat_id: UUID, outgoing: Outgoing, attempt_key: str
    ) -> Attempt:
        remembered = await self.chats.find_attempt(owner_id, chat_id, attempt_key)
        if remembered is not None:
            return remembered
        started = self._now()
        question = Question.parse(outgoing.text)
        model = ListedModel.parse(outgoing.model, outgoing.model_present)
        mode = LearningMode.parse(outgoing.mode, outgoing.mode_present).require_grounded()
        chat = await self._askable(owner_id, chat_id)
        pieces = await self.search.matching(chat.document_id, question.text)
        updated, attempt = await self._attempt(
            chat, question.text, model.value, mode.value, pieces, started
        )
        await self.chats.save(owner_id, updated)
        await self.chats.save_attempt(owner_id, chat_id, attempt_key, attempt)
        return attempt

    async def _askable(self, owner_id: UUID, chat_id: UUID) -> Chat:
        found = await self.chats.get(owner_id, chat_id)
        if found is None:
            raise ChatNotFound()
        ready = await self.search.ready(found.document_id)
        chat = found.with_vectors(ready)
        if not chat.askable():
            raise NotAskable()
        return chat

    async def _attempt(
        self,
        chat: Chat,
        question: str,
        model: str,
        mode: str,
        pieces: tuple[Source, ...],
        started,
    ) -> tuple[Chat, Attempt]:
        sources = Source.cite(pieces)
        if not sources:
            updated, lines = chat.record_missing(question, mode)
            return updated, Attempt(chat.id, lines)
        if expired(started, self._now(), self.latency):
            updated, lines = chat.record_failed(question)
            return updated, Attempt(chat.id, lines, ReplyError.failed())
        try:
            text = await asyncio.wait_for(
                self.tutor.answer(model, mode, question, sources),
                timeout=max(remaining_seconds(started, self._now(), self.latency), 0),
            )
        except (ReplyFailed, asyncio.TimeoutError):
            updated, lines = chat.record_failed(question)
            return updated, Attempt(chat.id, lines, ReplyError.failed())
        if expired(started, self._now(), self.latency):
            updated, lines = chat.record_failed(question)
            return updated, Attempt(chat.id, lines, ReplyError.failed())
        updated, lines = chat.record_grounded(question, model, mode, sources, text)
        return updated, Attempt(chat.id, lines)

    def _now(self):
        if self.clock is None:
            from datetime import datetime, timezone

            return datetime.now(timezone.utc)
        return self.clock.now()
