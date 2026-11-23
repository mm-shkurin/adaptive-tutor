from dataclasses import dataclass, replace
from uuid import UUID, uuid4

from domain.document.document import Document
from domain.quiz.attempt import Answer, Attempt, Score
from domain.quiz.errors import DocumentNotReady, InvalidChoice, NoOpenAttempt, Unanswered
from domain.quiz.question import Question
from domain.quiz.topic import Topic


@dataclass(frozen=True)
class Quiz:
    id: UUID
    document_id: UUID
    document_name: str
    topic: str
    questions: tuple[Question, ...]
    open_attempt: Attempt | None
    last_score: Score | None
    done: tuple[Answer, ...] = ()

    @staticmethod
    def require_ready(document: Document) -> None:
        if not document.is_ready():
            raise DocumentNotReady()

    @staticmethod
    def start(document: Document, topic: Topic, questions: tuple[Question, ...]) -> "Quiz":
        Quiz.require_ready(document)
        return Quiz(
            id=uuid4(),
            document_id=document.id,
            document_name=document.name,
            topic=topic.text,
            questions=questions,
            open_attempt=Attempt.start(),
            last_score=None,
        )

    def answer(self, choice_id: str) -> "Quiz":
        attempt = self._open()
        question = self.questions[attempt.index]
        if attempt.answered(question.id):
            return self
        if not isinstance(choice_id, str) or not question.allows(choice_id):
            raise InvalidChoice()
        return replace(self, open_attempt=attempt.with_choice(question.id, choice_id))

    def advance(self) -> "Quiz":
        attempt = self._open()
        question = self.questions[attempt.index]
        if not attempt.answered(question.id):
            raise Unanswered()
        if attempt.index + 1 < len(self.questions):
            return replace(self, open_attempt=attempt.next())
        return replace(
            self,
            open_attempt=None,
            last_score=attempt.score(self.questions),
            done=attempt.answers,
        )

    def retry(self) -> "Quiz":
        return replace(self, open_attempt=Attempt.start())

    def status(self) -> str:
        return "take" if self.open_attempt is not None else "result"

    def card(self) -> dict:
        score = None if self.last_score is None else self.last_score.json()
        return {
            "id": str(self.id),
            "document_id": str(self.document_id),
            "document_name": self.document_name,
            "topic": self.topic,
            "question_count": len(self.questions),
            "last_score": score,
        }

    def detail(self) -> dict:
        shown = self._shown()
        body = {
            **self.card(),
            "status": self.status(),
            "questions": [question.reveal(shown.get(question.id)) for question in self.questions],
        }
        if self.open_attempt is not None:
            body["current_index"] = self.open_attempt.index
        return body

    def _shown(self) -> dict:
        answers = self.open_attempt.answers if self.open_attempt is not None else self.done
        return {answer.question_id: answer for answer in answers}

    def _open(self) -> Attempt:
        if self.open_attempt is None:
            raise NoOpenAttempt()
        return self.open_attempt
