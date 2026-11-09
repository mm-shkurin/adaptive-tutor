import asyncio

from usecase.document.errors import InvalidDocument


class ProbeVirusCheck:
    def __init__(self, probe):
        self._probe = probe

    async def clear(self, content: bytes) -> None:
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
