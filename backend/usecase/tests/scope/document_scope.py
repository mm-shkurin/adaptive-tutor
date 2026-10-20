from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DocumentScope:
    person_id: UUID
    neighbour_id: UUID
    lecture_name: str
    neighbour_name: str

    DEFAULTS = {
        "person_id": UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        "neighbour_id": UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        "lecture_name": "lecture.pdf",
        "neighbour_name": "neighbour.pdf",
    }

    @classmethod
    def builder(cls, **overrides) -> "DocumentScope":
        return cls(**{**cls.DEFAULTS, **overrides})
