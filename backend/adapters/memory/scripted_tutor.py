from dataclasses import dataclass

from domain.chat.source import Source


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

    def script(self, text: str) -> None:
        self.text = text

    async def answer(self, model: str, mode: str, question: str, sources: tuple[Source, ...]) -> str:
        self.calls.append(TutorCall(model, mode, question, sources))
        return self.text
