from dataclasses import dataclass
from uuid import UUID

from domain.chat.chat import Chat


@dataclass(frozen=True)
class SendSnapshot:
    withholding: bool
    open_question_id: UUID | None

    @staticmethod
    def of(chat: Chat) -> "SendSnapshot":
        return SendSnapshot(chat.is_withholding(), chat.open_question_id())

    def missed(self, chat: Chat):
        from usecase.chat.send_message import Attempt

        if self.withholding and not chat.is_withholding():
            release = chat.last_release()
            if release is None:
                return Attempt(chat.id, (), persist=False)
            return Attempt(chat.id, (release,), persist=False)
        if self.open_question_id is None:
            return None
        open_id = chat.open_question_id()
        if open_id is not None and open_id == self.open_question_id:
            return None
        grade = chat.last_examiner_grade()
        if grade is None:
            return Attempt(chat.id, (), persist=False)
        return Attempt(chat.id, (grade,), persist=False)
