import asyncio
from dataclasses import dataclass

from domain.chat.source import Source
from usecase.chat.errors import ReplyFailed


class _CallHold:
    def __init__(self):
        self._entered = asyncio.Event()
        self._release = asyncio.Event()

    async def wait(self) -> None:
        self._entered.set()
        await self._release.wait()

    async def until_entered(self) -> None:
        await self._entered.wait()

    def release(self) -> None:
        self._release.set()


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
    def __init__(self, api_key: str = "test"):
        self.api_key = api_key
        self.text = ""
        self.calls: list[TutorCall] = []
        self.live = 0
        self._fail = False
        self._hang = False
        self._hold = None
        self._hold_each = False
        self._each_holds: list = []
        self._script_queue: list[str] = []
        self.finished = False
        self._clock = None
        self._moment = None

    def script(self, text: str) -> None:
        self._fail = False
        self._hang = False
        self._hold = None
        self._hold_each = False
        self._each_holds = []
        self._script_queue = []
        self.finished = False
        self._clock = None
        self._moment = None
        self.text = text

    def fail(self) -> None:
        self._fail = True
        self._hang = False
        self._hold = None
        self._hold_each = False

    def hang(self) -> None:
        self._fail = False
        self._hang = True
        self._hold = None
        self._hold_each = False
        self.finished = False

    def hold(self, latch) -> None:
        self._fail = False
        self._hang = False
        self._hold_each = False
        self._hold = latch
        self.finished = False

    def hold_each(self, texts: tuple[str, ...] = ()) -> None:
        self._fail = False
        self._hang = False
        self._hold = None
        self._hold_each = True
        self._each_holds = []
        self._script_queue = list(texts)
        self.finished = False

    def release_call(self, index: int) -> None:
        self._each_holds[index].release()

    def set_clock_on_answer(self, clock, moment) -> None:
        self._clock = clock
        self._moment = moment

    def _next_text(self) -> str:
        if self._script_queue:
            return self._script_queue.pop(0)
        return self.text

    async def answer(self, model: str, mode: str, question: str, sources: tuple[Source, ...]) -> str:
        self.live += 1
        try:
            self.calls.append(TutorCall(model, mode, question, sources))
            if self._clock is not None and self._moment is not None:
                self._clock.moment = self._moment
            if self._fail:
                raise ReplyFailed()
            if not self.api_key:
                raise ReplyFailed()
            if self._hold_each:
                latch = _CallHold()
                self._each_holds.append(latch)
                text = self._next_text()
                await latch.wait()
                self.finished = True
                return text
            if self._hold is not None:
                await self._hold.wait()
                self.finished = True
                return self._next_text()
            if self._hang:
                try:
                    await asyncio.sleep(30)
                except asyncio.CancelledError:
                    raise
                self.finished = True
                return self._next_text()
            self.finished = True
            return self._next_text()
        finally:
            self.live -= 1
