import asyncio
from dataclasses import dataclass
from datetime import timedelta
from uuid import UUID

from domain.chat.chat import Chat, NotAskable, TellUnavailable
from domain.chat.learning import LearningMode, Question
from domain.chat.line import Line
from domain.chat.source import Source
from usecase.chat.errors import ChatNotFound, ReplyFailed
from usecase.chat.examiner_turn import examiner_or_choice
from usecase.chat.outgoing import Outgoing
from usecase.chat.ports import ChatStore, MaterialSearch, Tutor
from usecase.chat.reply_budget import CHAT_LATENCY, expired, remaining_seconds
from usecase.chat.send_build import build_attempt
from usecase.chat.send_socratic import release, socratic


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
    persist: bool = True


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

        return await self.chats.with_attempt(
            owner_id,
            chat_id,
            attempt_key,
            lambda: build_attempt(self, owner_id, chat_id, outgoing, attempt_key, started),
        )

    async def _spoken(self, chat: Chat, outgoing: Outgoing, model: str, started) -> Attempt:
        answer = lambda m, mode, q, sources: self._answer(m, mode, q, sources, started)
        routed = await examiner_or_choice(chat, outgoing, model, self.search, answer)
        if routed is not None:
            return routed
        mode = LearningMode.parse(outgoing.mode, outgoing.mode_present)
        question = Question.parse(outgoing.text)
        if chat.is_withholding():
            return await release(self, chat, question.text, model, "socratic", started)
        if mode.value == "socratic":
            return await socratic(self, chat, question.text, model, started)
        mode.require_grounded()
        pieces = await self._match(chat, question.text)
        if pieces is None:
            _updated, lines = chat.record_failed(question.text)
            return Attempt(chat.id, lines, ReplyError.failed())
        _updated, attempt = await self._grounded(
            chat, question.text, model, mode.value, pieces, started
        )
        return attempt

    async def _tell(self, chat: Chat, model: str, started) -> Attempt:
        if chat.examiner_series_stopped() and not chat.is_withholding():
            return Attempt(chat.id, ())
        if not chat.is_withholding():
            raise TellUnavailable()
        prompt = chat.withheld_prompt() or ""
        return await release(self, chat, None, model, "socratic", started, prompt)

    async def _match(self, chat: Chat, question: str) -> tuple[Source, ...] | None:
        try:
            return await self.search.matching(chat.document_id, question)
        except ReplyFailed:
            return None

    async def _askable(self, owner_id: UUID, chat_id: UUID) -> Chat:
        found = await self.chats.get(owner_id, chat_id)
        if found is None:
            raise ChatNotFound()
        ready = await self.search.ready(found.document_id)
        chat = found.with_vectors(ready)
        if not chat.askable():
            raise NotAskable()
        return chat

    async def _grounded(
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
        text = await self._answer(model, mode, question, sources, started)
        if text is None:
            updated, lines = chat.record_failed(question)
            return updated, Attempt(chat.id, lines, ReplyError.failed())
        updated, lines = chat.record_grounded(question, model, mode, sources, text)
        return updated, Attempt(chat.id, lines)

    async def _answer(
        self,
        model: str,
        mode: str,
        question: str,
        sources: tuple[Source, ...],
        started,
    ) -> str | None:
        if expired(started, self._now(), self.latency):
            return None
        try:
            text = await asyncio.wait_for(
                self.tutor.answer(model, mode, question, sources),
                timeout=max(remaining_seconds(started, self._now(), self.latency), 0),
            )
        except (ReplyFailed, asyncio.TimeoutError):
            return None
        if expired(started, self._now(), self.latency):
            return None
        return text

    def _now(self):
        if self.clock is None:
            from datetime import datetime, timezone

            return datetime.now(timezone.utc)
        return self.clock.now()
