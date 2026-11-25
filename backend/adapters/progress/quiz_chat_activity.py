from uuid import UUID

from usecase.quiz.ports import QuizStore


class QuizChatActivity:
    def __init__(self, quizzes: QuizStore, chats):
        self.quizzes = quizzes
        self.chats = chats

    async def quiz_finishes(self, owner_id: UUID):
        return await self.quizzes.finishes_for(owner_id)

    async def chat_person_sends(self, owner_id: UUID):
        return await self.chats.person_send_times(owner_id)