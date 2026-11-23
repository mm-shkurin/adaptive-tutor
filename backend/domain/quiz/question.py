import unicodedata
from dataclasses import dataclass
from uuid import UUID, uuid4

from domain.chat.source import Source
from domain.quiz.attempt import Answer
from domain.quiz.choice import Choice
from domain.quiz.errors import GenerationFailed


@dataclass(frozen=True)
class Question:
    id: UUID
    text: str
    choices: tuple[Choice, ...]
    correct_choice_id: str
    page: int

    def allows(self, choice_id: str) -> bool:
        return any(choice.id == choice_id for choice in self.choices)

    def reveal(self, answer: Answer | None) -> dict:
        shown = {
            "id": str(self.id),
            "text": self.text,
            "choices": [{"id": choice.id, "text": choice.text} for choice in self.choices],
            "chosen_choice_id": None,
            "correct_choice_id": None,
            "correct": None,
            "page": None,
        }
        if answer is None:
            return shown
        shown["chosen_choice_id"] = answer.choice_id
        shown["correct_choice_id"] = self.correct_choice_id
        shown["correct"] = answer.choice_id == self.correct_choice_id
        shown["page"] = self.page
        return shown

    @staticmethod
    def assemble(count: int, pieces: tuple[Source, ...], payload: object) -> tuple["Question", ...]:
        raw = _questions(payload)
        if len(raw) != count:
            raise GenerationFailed()
        pages = {piece.page for piece in pieces if type(piece.page) is int and piece.page >= 1}
        return tuple(_question(item, pages) for item in raw)


def _questions(payload: object) -> list:
    if not isinstance(payload, dict):
        raise GenerationFailed()
    raw = payload.get("questions")
    if not isinstance(raw, list):
        raise GenerationFailed()
    return raw


def _question(item: object, pages: set[int]) -> Question:
    if not isinstance(item, dict):
        raise GenerationFailed()
    choices = _choices(item.get("choices"))
    index = _correct_index(item.get("correct_index"))
    return Question(
        id=uuid4(),
        text=_text(item.get("text")),
        choices=choices,
        correct_choice_id=choices[index].id,
        page=_page(item.get("page"), pages),
    )


def _choices(raw: object) -> tuple[Choice, ...]:
    if not isinstance(raw, list) or len(raw) != 4:
        raise GenerationFailed()
    return tuple(Choice(str(uuid4()), _text(text)) for text in raw)


def _text(raw: object) -> str:
    if not isinstance(raw, str):
        raise GenerationFailed()
    text = unicodedata.normalize("NFC", raw).strip()
    if text == "":
        raise GenerationFailed()
    return text


def _correct_index(raw: object) -> int:
    if type(raw) is not int or raw not in range(4):
        raise GenerationFailed()
    return raw


def _page(raw: object, pages: set[int]) -> int:
    if type(raw) is not int or raw not in pages:
        raise GenerationFailed()
    return raw
