from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class FakeFormulaAssist:
    results: dict[UUID, tuple[str, str]] = field(default_factory=dict)
    failures: set[UUID] = field(default_factory=set)
    calls: list[UUID] = field(default_factory=list)

    def set_result(self, slide_id: UUID, phrase: str, latex: str) -> None:
        self.results[slide_id] = (phrase, latex)

    def set_failure(self, slide_id: UUID) -> None:
        self.failures.add(slide_id)

    async def enrich(self, slide_id: UUID, content: bytes, ocr_text: str) -> tuple[str, str] | None:
        self.calls.append(slide_id)
        if slide_id in self.failures:
            raise TimeoutError("formula assist timed out")
        return self.results.get(slide_id)
