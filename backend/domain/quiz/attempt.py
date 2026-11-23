from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Answer:
    question_id: UUID
    choice_id: str


@dataclass(frozen=True)
class Score:
    correct: int
    total: int

    def json(self) -> dict:
        return {"correct": self.correct, "total": self.total}


@dataclass(frozen=True)
class Attempt:
    index: int
    answers: tuple[Answer, ...]

    @staticmethod
    def start() -> "Attempt":
        return Attempt(0, ())

    def answered(self, question_id: UUID) -> bool:
        return any(answer.question_id == question_id for answer in self.answers)

    def with_choice(self, question_id: UUID, choice_id: str) -> "Attempt":
        return Attempt(self.index, self.answers + (Answer(question_id, choice_id),))

    def next(self) -> "Attempt":
        return Attempt(self.index + 1, self.answers)

    def score(self, questions: tuple) -> Score:
        correct_ids = {question.id: question.correct_choice_id for question in questions}
        correct = sum(
            1 for answer in self.answers if correct_ids[answer.question_id] == answer.choice_id
        )
        return Score(correct, len(questions))
