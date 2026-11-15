from dataclasses import dataclass

REPLY_SOURCE_LIMIT = 10


@dataclass(frozen=True)
class Source:
    page: int | None
    text: str

    def json(self) -> dict:
        return {"page": self.page, "text": self.text}

    @staticmethod
    def cite(pieces: tuple["Source", ...]) -> tuple["Source", ...]:
        return pieces[:REPLY_SOURCE_LIMIT]
