import json
import re

import httpx

from domain.chat.source import Source
from domain.quiz.errors import GenerationFailed

_SYSTEM = (
    "You write a quiz grounded only in the supplied material. "
    "Output one JSON object only — no markdown fences, no prose before or after. "
    "Use the same language as the Topic. "
    'Required shape: {"questions":[{"text":"...","choices":["A","B","C","D"],'
    '"correct_index":0,"page":1}]}. '
    "Write exactly the requested number of questions. "
    "Each question has exactly four non-empty choice strings. "
    "correct_index is an integer 0..3. "
    "page must be one of the page numbers listed in the material lines."
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
            raw = await self._completion(model, topic, count, pieces)
            return normalize_quiz_payload(raw, count, pieces)
        except (httpx.HTTPError, KeyError, TypeError, ValueError, IndexError) as error:
            raise GenerationFailed() from error

    async def _completion(
        self, model: str, topic: str, count: int, pieces: tuple[Source, ...]
    ) -> dict:
        response = await self._post(_body(model, topic, count, pieces, json_mode=True))
        if not _ok(response):
            response = await self._post(_body(model, topic, count, pieces, json_mode=False))
        if not _ok(response):
            raise GenerationFailed()
        return _json_object(_assistant_text(response.json()))

    async def _post(self, body: dict) -> httpx.Response:
        async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
            return await client.post(
                self._url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self._api_key}",
                },
                json=body,
            )


def normalize_quiz_payload(payload: object, count: int, pieces: tuple[Source, ...]) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("object")
    questions = payload.get("questions")
    if not isinstance(questions, list) or len(questions) < count:
        raise ValueError("count")
    pages = _pages(pieces)
    default_page = pages[0] if pages else None
    fixed = [_normalize_question(item, pages, default_page) for item in questions[:count]]
    return {"questions": fixed}


def _body(
    model: str, topic: str, count: int, pieces: tuple[Source, ...], json_mode: bool
) -> dict:
    body = {
        "model": model,
        "max_tokens": 1800,
        "messages": [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": _user(topic, count, pieces)},
        ],
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    return body


def _user(topic: str, count: int, pieces: tuple[Source, ...]) -> str:
    material = "\n".join(_line(piece) for piece in pieces) if pieces else "(no material)"
    pages = ", ".join(str(page) for page in _pages(pieces)) or "(none)"
    return (
        f"Topic:\n{topic}\n\nQuestion count:\n{count}\n\n"
        f"Allowed pages:\n{pages}\n\nMaterial:\n{material}\n\n"
        "Return only the JSON object. Every page must be one of the Allowed pages."
    )


def _line(piece: Source) -> str:
    page = f"page {piece.page}" if piece.page is not None else "no page"
    return f"[{page}] {piece.text}"


def _pages(pieces: tuple[Source, ...]) -> list[int]:
    return sorted({piece.page for piece in pieces if type(piece.page) is int and piece.page >= 1})


def _ok(response: httpx.Response) -> bool:
    return 200 <= response.status_code < 300


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
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match is None:
            raise ValueError("json")
        parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise ValueError("object")
    return parsed


def _normalize_question(item: object, pages: list[int], default_page: int | None) -> dict:
    if not isinstance(item, dict):
        raise ValueError("item")
    index = _as_int(item.get("correct_index"))
    page = _as_int(item.get("page"))
    if page not in pages:
        if default_page is None:
            raise ValueError("page")
        page = default_page
    return {
        "text": item.get("text"),
        "choices": item.get("choices"),
        "correct_index": index,
        "page": page,
    }


def _as_int(raw: object) -> int:
    if type(raw) is int:
        return raw
    if type(raw) is float and raw == int(raw):
        return int(raw)
    if isinstance(raw, str) and raw.strip().lstrip("-").isdigit():
        return int(raw.strip())
    raise ValueError("int")
