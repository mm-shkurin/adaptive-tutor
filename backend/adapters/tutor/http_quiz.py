import json

import httpx

from domain.chat.source import Source
from domain.quiz.errors import GenerationFailed

_SYSTEM = (
    "You write a quiz grounded only in the supplied material. "
    "Reply with JSON only, no markdown. Use the same language as the Topic. "
    'Shape: {"questions":[{"text":"...","choices":["","","",""],"correct_index":0,"page":1}]}. '
    "Write exactly the requested number of questions. "
    "Each question has exactly four choices and one correct_index from 0 to 3. "
    "Each page must be a page number from the material."
)


class HttpQuiz:
    def __init__(self, base_url: str, api_key: str, timeout: float = 5, transport=None):
        self._url = base_url.rstrip("/") + "/chat/completions"
        self._api_key = api_key
        self._timeout = timeout
        self._transport = transport

    async def compose(self, model: str, topic: str, count: int, pieces: tuple[Source, ...]) -> object:
        if not self._api_key:
            raise GenerationFailed()
        try:
            response = await self._post(_body(model, topic, count, pieces))
        except httpx.HTTPError as error:
            raise GenerationFailed() from error
        if not 200 <= response.status_code < 300:
            raise GenerationFailed()
        try:
            return _json_object(_assistant_text(response.json()))
        except (KeyError, TypeError, ValueError, IndexError) as error:
            raise GenerationFailed() from error

    async def _post(self, body: dict) -> httpx.Response:
        async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
            return await client.post(
                self._url,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {self._api_key}"},
                json=body,
            )


def _body(model: str, topic: str, count: int, pieces: tuple[Source, ...]) -> dict:
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": _user(topic, count, pieces)},
        ],
    }


def _user(topic: str, count: int, pieces: tuple[Source, ...]) -> str:
    material = "\n".join(_line(piece) for piece in pieces) if pieces else "(no material)"
    return (
        f"Topic:\n{topic}\n\nQuestion count:\n{count}\n\nMaterial:\n{material}\n\n"
        "Write the quiz in the same language as the Topic."
    )


def _line(piece: Source) -> str:
    page = f"page {piece.page}" if piece.page is not None else "no page"
    return f"[{page}] {piece.text}"


def _assistant_text(body: object) -> str:
    if not isinstance(body, dict):
        raise ValueError("body")
    content = body["choices"][0]["message"]["content"]
    if not isinstance(content, str) or content.strip() == "":
        raise ValueError("empty")
    return content


def _json_object(content: str) -> dict:
    text = content.strip()
    if text.startswith("```"):
        text = "\n".join(line for line in text.splitlines() if not line.startswith("```")).strip()
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("object")
    return parsed
