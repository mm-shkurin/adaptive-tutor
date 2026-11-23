from uuid import UUID

from usecase.quiz.ports import QuizStore


class QuizWipe:
    def __init__(self, quizzes: QuizStore):
        self.quizzes = quizzes

    async def wipe(self, owner_id: UUID | None) -> None:
        if owner_id is None:
            return
        await self.quizzes.delete_owned(owner_id)
