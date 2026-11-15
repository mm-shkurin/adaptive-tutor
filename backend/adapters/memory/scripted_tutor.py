import asyncio
from dataclasses import dataclass

from domain.chat.source import Source
from usecase.chat.errors import ReplyFailed


@dataclass(frozen=True)
class TutorCall:
    model: str
    mode: str
    question: str
    sources: tuple[Source, ...]

    def json(self) -> dict:
        return {
            "model": self.model,
            "mode": self.mode,
            "question": self.question,
            "sources": [source.json() for source in self.sources],
        }


class ScriptedTutor:
    def __init__(self):
        self.text = ""
        self.calls: list[TutorCall] = []
        self._fail = False
        self._hang = False
        self.finished = False
        self._clock = None
        self._moment = None

    def script(self, text: str) -> None:
        self._fail = False
        self._hang = False
        self.finished = False
        self._clock = None
        self._moment = None
        self.text = text

    def fail(self) -> None:
        self._fail = True
        self._hang = False

    def hang(self) -> None:
        self._fail = False
        self._hang = True
        self.finished = False

    def set_clock_on_answer(self, clock, moment) -> None:
        self._clock = clock
        self._moment = moment

    async def answer(self, model: str, mode: str, question: str, sources: tuple[Source, ...]) -> str:
        self.calls.append(TutorCall(model, mode, question, sources))
        if self._clock is not None and self._moment is not None:
            self._clock.moment = self._moment
        if self._fail:
            raise ReplyFailed()
        if self._hang:
            try:
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                raise
            self.finished = True
            return self.text
        self.finished = True
        return self.text
