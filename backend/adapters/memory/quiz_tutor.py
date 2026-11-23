from dataclasses import dataclass

from domain.chat.source import Source
from domain.quiz.errors import GenerationFailed


@dataclass(frozen=True)
class QuizCall:
    model: str
    topic: str
    count: int
    pieces: tuple[Source, ...]


class ScriptedQuizTutor:
    def __init__(self):
        self.calls: list[QuizCall] = []
        self.payload = None
        self._fail = False
        self._entered = None
        self._release = None

    def script(self, payload: dict) -> None:
        self.payload = payload
        self._fail = False

    def fail(self) -> None:
        self._fail = True

    def hold(self, entered, release) -> None:
        self._entered = entered
        self._release = release

    async def compose(self, model: str, topic: str, count: int, pieces: tuple[Source, ...]) -> object:
        self.calls.append(QuizCall(model, topic, count, pieces))
        if self._release is not None:
            if self._entered is not None and not self._entered.is_set():
                self._entered.set()
            await self._release.wait()
        if self._fail or self.payload is None:
            raise GenerationFailed()
        return self.payload
