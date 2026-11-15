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

    def script(self, text: str) -> None:
        self._fail = False
        self.text = text

    def fail(self) -> None:
        self._fail = True

    async def answer(self, model: str, mode: str, question: str, sources: tuple[Source, ...]) -> str:
        self.calls.append(TutorCall(model, mode, question, sources))
        if self._fail:
            raise ReplyFailed()
        return self.text
