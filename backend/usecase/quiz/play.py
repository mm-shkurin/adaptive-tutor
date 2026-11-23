from uuid import UUID

from usecase.quiz.ports import QuizStore


class AnswerQuiz:
    def __init__(self, quizzes: QuizStore):
        self.quizzes = quizzes

    async def answer(self, owner_id: UUID, quiz_id: UUID, choice_id: str):
        return await self.quizzes.update(owner_id, quiz_id, lambda quiz: quiz.answer(choice_id))


class AdvanceQuiz:
    def __init__(self, quizzes: QuizStore):
        self.quizzes = quizzes

    async def advance(self, owner_id: UUID, quiz_id: UUID):
        return await self.quizzes.update(owner_id, quiz_id, lambda quiz: quiz.advance())


class RetryQuiz:
    def __init__(self, quizzes: QuizStore):
        self.quizzes = quizzes

    async def retry(self, owner_id: UUID, quiz_id: UUID):
        return await self.quizzes.update(owner_id, quiz_id, lambda quiz: quiz.retry())
