from dataclasses import dataclass, replace
from uuid import UUID, uuid4

from domain.chat.choice import Choice
from domain.chat.line import Line
from domain.chat.source import Source
from domain.document.document import Document

NOT_ASKABLE_NOTICE = "Материал пока нельзя спросить."


class DocumentNotReady(Exception):
    """A chat binds only a ready PDF."""


class NotAskable(Exception):
    """This material has no vectors yet."""


class TellUnavailable(Exception):
    """Tell needs an open withheld question."""


class ChoiceRequired(Exception):
    """An open examiner question needs a choice_id."""


class ChoiceUnknown(Exception):
    """The choice_id is not one of the open question's choices."""


EXAMINER_SERIES = 3


@dataclass(frozen=True)
class Chat:
    id: UUID
    document_id: UUID
    document_name: str
    vectors_ready: bool
    lines: tuple[Line, ...] = ()

    @staticmethod
    def bound_to(document: Document) -> "Chat":
        if not document.is_ready():
            raise DocumentNotReady()
        return Chat(
            id=uuid4(),
            document_id=document.id,
            document_name=document.name,
            vectors_ready=False,
        )

    @staticmethod
    def stored(
        chat_id: UUID,
        document_id: UUID,
        document_name: str,
        lines: tuple[Line, ...] = (),
    ) -> "Chat":
        return Chat(chat_id, document_id, document_name, vectors_ready=False, lines=lines)

    def with_vectors(self, ready: bool) -> "Chat":
        return replace(self, vectors_ready=ready)

    def preview(self) -> str | None:
        spoken = tuple(line.text for line in self.lines if line.role == "person")
        if not spoken:
            return None
        return spoken[-1]

    def askable(self) -> bool:
        return self.vectors_ready

    def notice(self) -> str | None:
        if self.vectors_ready:
            return None
        return NOT_ASKABLE_NOTICE

    def record_grounded(
        self,
        question: str,
        model: str,
        mode: str,
        sources: tuple[Source, ...],
        tutor_text: str,
    ) -> tuple["Chat", tuple[Line, Line]]:
        person = Line.person(question)
        tutor = Line.grounded(tutor_text, model, mode, sources)
        return replace(self, lines=self.lines + (person, tutor)), (person, tutor)

    def record_missing(self, question: str, mode: str) -> tuple["Chat", tuple[Line, Line]]:
        person = Line.person(question)
        tutor = Line.missing(mode)
        return replace(self, lines=self.lines + (person, tutor)), (person, tutor)

    def record_failed(self, question: str) -> tuple["Chat", tuple[Line, ...]]:
        person = Line.person(question)
        return replace(self, lines=self.lines + (person,)), (person,)

    def record_withheld(
        self, question: str, mode: str, tutor_text: str
    ) -> tuple["Chat", tuple[Line, Line]]:
        person = Line.person(question)
        tutor = Line.withheld(tutor_text, mode)
        return replace(self, lines=self.lines + (person, tutor)), (person, tutor)

    def record_release(
        self,
        try_text: str | None,
        model: str,
        mode: str,
        sources: tuple[Source, ...],
        tutor_text: str,
    ) -> tuple["Chat", tuple[Line, ...]]:
        tutor = Line.grounded(tutor_text, model, mode, sources)
        if try_text is None:
            return replace(self, lines=self.lines + (tutor,)), (tutor,)
        person = Line.person(try_text)
        return replace(self, lines=self.lines + (person, tutor)), (person, tutor)

    def is_withholding(self) -> bool:
        for line in reversed(self.lines):
            if line.role == "tutor":
                return line.kind == "withheld"
        return False

    def withheld_prompt(self) -> str | None:
        prompt = None
        previous = None
        for line in self.lines:
            if line.role == "tutor" and line.kind == "withheld" and previous is not None:
                if previous.role == "person":
                    prompt = previous.text
            previous = line
        return prompt

    def open_examiner_question(self) -> Line | None:
        for line in reversed(self.lines):
            if line.role == "tutor" and line.kind == "question":
                return line
            if line.role == "tutor" and line.kind == "grade":
                return None
        return None

    def record_examiner_question(
        self, text: str, choices: tuple[Choice, ...], supported_choice_id: str
    ) -> tuple["Chat", tuple[Line, ...]]:
        tutor = Line.question(text, "examiner", choices, supported_choice_id)
        return replace(self, lines=self.lines + (tutor,)), (tutor,)

    def examiner_grade_count(self) -> int:
        return sum(1 for line in self.lines if line.role == "tutor" and line.kind == "grade")

    def examiner_series_stopped(self) -> bool:
        return self.examiner_grade_count() >= EXAMINER_SERIES

    def last_examiner_grade(self) -> Line | None:
        for line in reversed(self.lines):
            if line.role == "tutor" and line.kind == "grade":
                return line
        return None

    def require_examiner_choice(self, choice_id: object) -> str:
        question = self.open_examiner_question()
        if question is None:
            raise ChoiceUnknown()
        if not isinstance(choice_id, str):
            raise ChoiceUnknown()
        allowed = {choice.id for choice in question.choices}
        if choice_id not in allowed:
            raise ChoiceUnknown()
        return choice_id

    def record_examiner_grade(
        self, choice_id: str, page: int | None
    ) -> tuple["Chat", tuple[Line, ...]]:
        question = self.open_examiner_question()
        if question is None:
            raise ChoiceUnknown()
        correct = choice_id == question.supported_choice_id
        tutor = Line.grade(choice_id, correct, page)
        return replace(self, lines=self.lines + (tutor,)), (tutor,)

    def with_appended(self, lines: tuple[Line, ...]) -> "Chat":
        return replace(self, lines=self.lines + lines)
