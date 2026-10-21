import unicodedata
from dataclasses import dataclass

KEPT_TOKENS = 500


@dataclass(frozen=True)
class ExtractedText:
    value: str

    @staticmethod
    def compose(raw: str) -> "ExtractedText":
        return ExtractedText(unicodedata.normalize("NFC", raw))

    def pieces(self) -> tuple[str, ...]:
        kept: list[str] = []
        pending: list[str] = []
        for paragraph in self.value.split("\n\n"):
            pending.append(paragraph)
            if _tokens(pending) >= KEPT_TOKENS:
                kept.append(_joined(pending))
                pending = []
        if pending:
            kept.append(_joined(pending))
        return tuple(kept)


def _joined(paragraphs: list[str]) -> str:
    return "\n\n".join(paragraphs)


def _tokens(paragraphs: list[str]) -> int:
    return len(_joined(paragraphs).split())
