from dataclasses import dataclass, replace
from uuid import UUID, uuid4


class InvalidStatusTransition(Exception):
    """The step skips or reverses indexing."""


@dataclass(frozen=True)
class Document:
    id: UUID
    name: str
    size_bytes: int
    page_count: int | None
    piece_count: int | None
    status: str
    error: str | None

    @staticmethod
    def accepted(name: str, size_bytes: int) -> "Document":
        return Document(
            id=uuid4(),
            name=name,
            size_bytes=size_bytes,
            page_count=None,
            piece_count=None,
            status="waiting",
            error=None,
        )

    def indexing(self) -> "Document":
        return replace(self, status="indexing")

    def waiting(self) -> "Document":
        return replace(self, status="waiting", error=None, page_count=None, piece_count=None)

    def ready(self, page_count: int, piece_count: int) -> "Document":
        return replace(self, status="ready", page_count=page_count, piece_count=piece_count, error=None)

    def failed(self, reason: str) -> "Document":
        return replace(self, status="failed", error=reason, page_count=None, piece_count=None)

    def is_finished(self) -> bool:
        return self.status in {"ready", "failed"}

    def is_ready(self) -> bool:
        return self.status == "ready"

    def transition(self, toward: str) -> "Document":
        if self.status == "waiting" and toward == "indexing":
            return self.indexing()
        if self.status == "indexing" and toward == "ready":
            return self.ready(self.page_count or 1, self.piece_count or 1)
        if self.status == "indexing" and toward == "failed":
            return self.failed("forced")
        raise InvalidStatusTransition()
