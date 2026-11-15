from dataclasses import dataclass
from uuid import UUID

from domain.chat.chat import Chat, NotAskable
from domain.chat.learning import LearningMode, ListedModel, Question
from domain.chat.line import Line
from domain.chat.source import Source
from usecase.chat.errors import ChatNotFound
from usecase.chat.outgoing import Outgoing
from usecase.chat.ports import ChatStore, MaterialSearch, Tutor


@dataclass(frozen=True)
class Attempt:
    chat_id: UUID
    lines: tuple[Line, ...]


class SendMessage:
    def __init__(self, chats: ChatStore, search: MaterialSearch, tutor: Tutor):
        self.chats = chats
        self.search = search
        self.tutor = tutor

    async def send(self, owner_id: UUID, chat_id: UUID, outgoing: Outgoing) -> Attempt:
        question = Question.parse(outgoing.text)
        model = ListedModel.parse(outgoing.model, outgoing.model_present)
        mode = LearningMode.parse(outgoing.mode, outgoing.mode_present).require_grounded()
        chat = await self._askable(owner_id, chat_id)
        pieces = await self.search.matching(chat.document_id, question.text)
        updated, lines = await self._record(chat, question.text, model.value, mode.value, Source.cite(pieces))
        await self.chats.save(owner_id, updated)
        return Attempt(updated.id, lines)

    async def _askable(self, owner_id: UUID, chat_id: UUID) -> Chat:
        found = await self.chats.get(owner_id, chat_id)
        if found is None:
            raise ChatNotFound()
        chat = found.with_vectors(await self.search.ready(found.document_id))
        if not chat.askable():
            raise NotAskable()
        return chat

    async def _record(
        self,
        chat: Chat,
        question: str,
        model: str,
        mode: str,
        sources: tuple[Source, ...],
    ) -> tuple[Chat, tuple[Line, Line]]:
        if not sources:
            return chat.record_missing(question, mode)
        text = await self.tutor.answer(model, mode, question, sources)
        return chat.record_grounded(question, model, mode, sources, text)
