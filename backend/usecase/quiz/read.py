from uuid import UUID

from usecase.quiz.errors import QuizNotFound
from usecase.quiz.ports import QuizStore


class ListQuizzes:
    def __init__(self, quizzes: QuizStore):
        self.quizzes = quizzes

    async def list(self, owner_id: UUID):
        return await self.quizzes.list_for(owner_id)


class GetQuiz:
    def __init__(self, quizzes: QuizStore):
        self.quizzes = quizzes

    async def open(self, owner_id: UUID, quiz_id: UUID):
        found = await self.quizzes.get(owner_id, quiz_id)
        if found is None:
            raise QuizNotFound()
        return found
