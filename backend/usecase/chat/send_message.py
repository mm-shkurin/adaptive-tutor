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
            return await self._release(chat, question.text, model, "socratic", started)
        if mode.value == "socratic":
            return await self._socratic(chat, question.text, model, started)
        mode.require_grounded()
        pieces = await self.search.matching(chat.document_id, question.text)
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
        return await self._release(chat, None, model, "socratic", started, prompt)

    async def _socratic(self, chat: Chat, question: str, model: str, started) -> Attempt:
        pieces = await self.search.matching(chat.document_id, question)
        sources = Source.cite(pieces)
        if not sources:
            _updated, lines = chat.record_missing(question, "socratic")
            return Attempt(chat.id, lines)
        text = await self._answer(model, "socratic", question, sources, started)
        if text is None:
            _updated, lines = chat.record_failed(question)
            return Attempt(chat.id, lines, ReplyError.failed())
        _updated, lines = chat.record_withheld(question, "socratic", text)
        return Attempt(chat.id, lines)

    async def _release(
        self,
        chat: Chat,
        try_text: str | None,
        model: str,
        mode: str,
        started,
        prompt: str | None = None,
    ) -> Attempt:
        ask = prompt if prompt is not None else (try_text or "")
        pieces = await self.search.matching(chat.document_id, ask)
        sources = Source.cite(pieces)
        if not sources:
            if try_text is None:
                return Attempt(chat.id, (Line.missing(mode),))
            _updated, lines = chat.record_missing(try_text, mode)
            return Attempt(chat.id, lines)
        text = await self._answer(model, mode, ask, sources, started)
        if text is None:
            if try_text is None:
                return Attempt(chat.id, (), ReplyError.failed())
            _updated, lines = chat.record_failed(try_text)
            return Attempt(chat.id, lines, ReplyError.failed())
        _updated, lines = chat.record_release(try_text, model, mode, sources, text)
        return Attempt(chat.id, lines)

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
