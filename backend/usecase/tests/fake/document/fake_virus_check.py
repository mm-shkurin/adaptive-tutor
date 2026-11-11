from usecase.document.errors import InvalidDocument

_EXTERNAL_CALL_DEADLINE_SECONDS = 0.12


class FakeVirusCheck:
    def __init__(self):
        self.scans = 0
        self.outcome = "clears"
        self._call_delay: float | None = None
        self._deadline = _EXTERNAL_CALL_DEADLINE_SECONDS

    def clear_files(self) -> None:
        self.outcome = "clears"
        self._call_delay = None

    def set_outcome(self, outcome: str) -> None:
        self.outcome = outcome

    def prepare_call(self) -> None:
        self._call_delay = None
        self.outcome = "clears"

    def finish_just_before_deadline(self) -> None:
        self._call_delay = self._deadline - 0.02
        self.outcome = "clears"

    def reach_deadline(self) -> None:
        self._call_delay = self._deadline + 0.02
        self.outcome = "clears"

    async def clear(self, content: bytes) -> None:
        self.scans += 1
        delay = 0.0 if self._call_delay is None else self._call_delay
        if delay >= self._deadline:
            raise InvalidDocument("virus_detected", "Virus detected")
        if self.outcome in {"finds_virus", "answers_unreadable", "times_out"}:
            raise InvalidDocument("virus_detected", "Virus detected")
