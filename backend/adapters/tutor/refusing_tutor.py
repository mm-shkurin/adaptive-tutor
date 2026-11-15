from domain.chat.source import Source
from usecase.chat.errors import ReplyFailed


class RefusingTutor:
    async def answer(self, model: str, mode: str, question: str, sources: tuple[Source, ...]) -> str:
        raise ReplyFailed()
