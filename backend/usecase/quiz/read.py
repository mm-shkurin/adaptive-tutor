from dataclasses import replace
from uuid import UUID

from domain.document.document import DELETED_SOURCE_NAME
from usecase.document.ports import DocumentIntake
from usecase.quiz.errors import QuizNotFound
from usecase.quiz.ports import QuizStore


class ListQuizzes:
    def __init__(self, quizzes: QuizStore, documents: DocumentIntake | None = None):
        self.quizzes = quizzes
        self.documents = documents

    async def list(self, owner_id: UUID):
        items = await self.quizzes.list_for(owner_id)
        if self.documents is None:
            return items
        return tuple([await self._named(owner_id, quiz) for quiz in items])

    async def _named(self, owner_id: UUID, quiz):
        found = await self.documents.get(owner_id, quiz.document_id)
        if found is None:
            return replace(quiz, document_name=DELETED_SOURCE_NAME)
        return quiz


class GetQuiz:
    def __init__(self, quizzes: QuizStore, documents: DocumentIntake | None = None):
        self.quizzes = quizzes
        self.documents = documents

    async def open(self, owner_id: UUID, quiz_id: UUID):
        found = await self.quizzes.get(owner_id, quiz_id)
        if found is None:
            raise QuizNotFound()
        if self.documents is None:
            return found
        material = await self.documents.get(owner_id, found.document_id)
        if material is None:
            return replace(found, document_name=DELETED_SOURCE_NAME)
        return found
