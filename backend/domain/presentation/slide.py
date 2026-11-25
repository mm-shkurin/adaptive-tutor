from dataclasses import dataclass, replace
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Slide:
    id: UUID
    position: int
    source: str
    text: str
    formula_phrase: str
    formula_latex: str
    empty: bool
    pdf_document_id: UUID | None
    pdf_page: int | None

    @staticmethod
    def image(position: int) -> "Slide":
        return Slide(
            id=uuid4(),
            position=position,
            source="image",
            text="",
            formula_phrase="",
            formula_latex="",
            empty=False,
            pdf_document_id=None,
            pdf_page=None,
        )

    def with_position(self, position: int) -> "Slide":
        return replace(self, position=position)

    def with_text(self, text: str, phrase: str = "", latex: str = "") -> "Slide":
        return replace(self, text=text, formula_phrase=phrase, formula_latex=latex)

    def mark_empty(self) -> "Slide":
        return replace(self, empty=True, text="")

    def mark_indexed(self, text: str, phrase: str = "", latex: str = "") -> "Slide":
        if text.strip() == "":
            return self.mark_empty()
        return replace(self, text=text, formula_phrase=phrase, formula_latex=latex, empty=False)

    def json(self) -> dict:
        return {
            "id": str(self.id),
            "position": self.position,
            "source": self.source,
            "text": self.text,
            "formula_phrase": self.formula_phrase or None,
            "formula_latex": self.formula_latex or None,
            "empty": self.empty,
            "pdf_document_id": str(self.pdf_document_id) if self.pdf_document_id else None,
            "pdf_page": self.pdf_page,
        }