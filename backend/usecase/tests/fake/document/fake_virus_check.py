from usecase.document.errors import InvalidDocument


class FakeVirusCheck:
    def __init__(self):
        self.scans = 0
        self.outcome = "clears"

    def clear_files(self) -> None:
        self.outcome = "clears"

    def set_outcome(self, outcome: str) -> None:
        self.outcome = outcome

    async def clear(self, content: bytes) -> None:
        self.scans += 1
        if self.outcome in {"finds_virus", "answers_unreadable", "times_out"}:
            raise InvalidDocument("virus_detected", "Virus detected")
