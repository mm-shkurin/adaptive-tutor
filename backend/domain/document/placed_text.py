from dataclasses import dataclass

from domain.document.extracted_text import KEPT_TOKENS


@dataclass(frozen=True)
class TextSpan:
    page: int
    text: str


@dataclass(frozen=True)
class PlacedPiece:
    text: str
    page: int | None


def place(spans: tuple[TextSpan, ...]) -> tuple[PlacedPiece, ...]:
    kept: list[PlacedPiece] = []
    pending: list[TextSpan] = []
    for span in spans:
        pending.append(span)
        tokens = _tokens(pending)
        if tokens == KEPT_TOKENS:
            kept.append(_placed(pending))
            pending = []
        elif tokens > KEPT_TOKENS:
            kept.append(_placed(pending[:-1]))
            pending = [pending[-1]]
    if pending:
        kept.append(_placed(pending))
    return tuple(kept)


def _placed(spans: list[TextSpan]) -> PlacedPiece:
    if not spans:
        return PlacedPiece("", None)
    return PlacedPiece("\n\n".join(span.text for span in spans), spans[0].page)


def _tokens(spans: list[TextSpan]) -> int:
    return len("\n\n".join(span.text for span in spans).split())
