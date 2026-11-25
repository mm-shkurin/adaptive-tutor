from dataclasses import dataclass

from domain.document.placed_text import PlacedPiece

REPLY_SOURCE_LIMIT = 10


@dataclass(frozen=True)
class Source:
    page: int | None
    text: str
    slide: int | None = None

    def json(self) -> dict:
        body = {"page": self.page, "text": self.text}
        if self.slide is not None:
            body["slide"] = self.slide
        return body

    @staticmethod
    def from_placed(piece: PlacedPiece) -> "Source":
        return Source(piece.page, piece.text, piece.slide)

    @staticmethod
    def cite(pieces: tuple["Source", ...]) -> tuple["Source", ...]:
        return pieces[:REPLY_SOURCE_LIMIT]
