from dataclasses import dataclass
from uuid import UUID

from domain.chat.chat import Chat, NotAskable
from domain.chat.learning import LearningMode, ListedModel, Question
from domain.chat.line import Line
from domain.chat.source import Source
from usecase.chat.errors import ChatNotFound, ReplyFailed
from usecase.chat.outgoing import Outgoing
from usecase.chat.ports import ChatStore, MaterialSearch, Tutor

REPLY_FAILED = {"code": "reply_failed", "message": "The model could not answer"}


@dataclass(frozen=True)
class Attempt:
    chat_id: UUID
    lines: tuple[Line, ...]
    error: dict | None = None


class SendMessage:
    def __init__(self, chats: ChatStore, search: MaterialSearch, tutor: Tutor):
        self.chats = chats
        self.search = search
        self.tutor = tutor

    async def send(
        self, owner_id: UUID, chat_id: UUID, outgoing: Outgoing, attempt_key: str
    ) -> Attempt:
        remembered = await self.chats.find_attempt(owner_id, chat_id, attempt_key)
        if remembered is not None:
            return remembered
        question = Question.parse(outgoing.text)
        model = ListedModel.parse(outgoing.model, outgoing.model_present)
        mode = LearningMode.parse(outgoing.mode, outgoing.mode_present).require_grounded()
        chat = await self._askable(owner_id, chat_id)
        pieces = await self.search.matching(chat.document_id, question.text)
        updated, attempt = await self._attempt(chat, question.text, model.value, mode.value, pieces)
        await self.chats.save(owner_id, updated)
        await self.chats.save_attempt(owner_id, chat_id, attempt_key, attempt)
        return attempt

    async def _askable(self, owner_id: UUID, chat_id: UUID) -> Chat:
        found = await self.chats.get(owner_id, chat_id)
        if found is None:
            raise ChatNotFound()
        chat = found.with_vectors(await self.search.ready(found.document_id))
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
    ) -> tuple[Chat, Attempt]:
        sources = Source.cite(pieces)
        if not sources:
            updated, lines = chat.record_missing(question, mode)
            return updated, Attempt(chat.id, lines)
        try:
            text = await self.tutor.answer(model, mode, question, sources)
        except ReplyFailed:
            updated, lines = chat.record_failed(question)
            return updated, Attempt(chat.id, lines, REPLY_FAILED)
        updated, lines = chat.record_grounded(question, model, mode, sources, text)
        return updated, Attempt(chat.id, lines)
