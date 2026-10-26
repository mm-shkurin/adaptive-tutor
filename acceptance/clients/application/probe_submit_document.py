import asyncio

from usecase.document.errors import InvalidDocument
from usecase.document.submit_document import SubmitDocument


class ProbeSubmitDocument(SubmitDocument):
    def __init__(self, intake, rates, probe):
        super().__init__(intake, rates)
        self._probe = probe

    async def submit(self, owner_id, name, content, submission_key):
        await self._virus_check()
        return await super().submit(owner_id, name, content, submission_key)

    async def _virus_check(self) -> None:
        delay = self._probe.virus_call_delay_seconds()
        if delay > 0:
            await asyncio.sleep(delay)
        self._probe.record_virus_scan()
        deadline = self._probe.external_call_deadline_seconds()
        if delay >= deadline:
            raise InvalidDocument("virus_detected", "Virus detected")
        outcome = self._probe.virus_outcome()
        if outcome in {"finds_virus", "answers_unreadable", "times_out"}:
            raise InvalidDocument("virus_detected", "Virus detected")
