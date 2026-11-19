from dataclasses import dataclass
from uuid import UUID, uuid4

from domain.chat.source import Source

NOT_IN_MATERIAL = "Этого нет в материале."


@dataclass(frozen=True)
class Line:
    id: UUID
    role: str
    text: str
    model: str | None
    mode: str | None
    kind: str | None
    page: int | None
    sources: tuple[Source, ...]

    @staticmethod
    def person(text: str) -> "Line":
        return Line(uuid4(), "person", text, None, None, None, None, ())

    @staticmethod
    def grounded(text: str, model: str, mode: str, sources: tuple[Source, ...]) -> "Line":
        return Line(uuid4(), "tutor", text, model, mode, "reply", sources[0].page, sources)

    @staticmethod
    def missing(mode: str) -> "Line":
        return Line(uuid4(), "tutor", NOT_IN_MATERIAL, None, mode, "reply", None, ())

    @staticmethod
    def withheld(text: str, mode: str) -> "Line":
        return Line(uuid4(), "tutor", text, None, mode, "withheld", None, ())

    def json(self) -> dict:
        return {
            "id": str(self.id),
            "role": self.role,
            "text": self.text,
            "model": self.model,
            "mode": self.mode,
            "kind": self.kind,
            "page": self.page,
            "sources": [source.json() for source in self.sources],
        }
