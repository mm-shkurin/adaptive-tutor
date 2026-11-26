from uuid import UUID


class NoopFormulaAssist:
    async def enrich(self, slide_id: UUID, content: bytes, ocr_text: str) -> tuple[str, str] | None:
        return None
