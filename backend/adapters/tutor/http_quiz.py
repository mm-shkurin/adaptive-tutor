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
    "page must be one of the page or slide numbers listed in the material lines."
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
    refs = _refs(pieces)
    default_ref = refs[0] if refs else None
    fixed = [_normalize_question(item, refs, default_ref) for item in questions[:count]]
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
    refs = ", ".join(str(ref) for ref in _refs(pieces)) or "(none)"
    return (
        f"Topic:\n{topic}\n\nQuestion count:\n{count}\n\n"
        f"Allowed citation numbers:\n{refs}\n\nMaterial:\n{material}\n\n"
        "Return only the JSON object. Every page field must be one of the Allowed citation numbers."
    )


def _line(piece: Source) -> str:
    labels: list[str] = []
    if type(piece.slide) is int and piece.slide >= 1:
        labels.append(f"slide {piece.slide}")
    if type(piece.page) is int and piece.page >= 1:
        labels.append(f"page {piece.page}")
    tag = ", ".join(labels) if labels else "no citation"
    return f"[{tag}] {piece.text}"


def _refs(pieces: tuple[Source, ...]) -> list[int]:
    refs: set[int] = set()
    for piece in pieces:
        if type(piece.page) is int and piece.page >= 1:
            refs.add(piece.page)
        if type(piece.slide) is int and piece.slide >= 1:
            refs.add(piece.slide)
    return sorted(refs)


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


def _normalize_question(item: object, refs: list[int], default_ref: int | None) -> dict:
    if not isinstance(item, dict):
        raise ValueError("item")
    index = _as_int(item.get("correct_index"))
    page = _as_int(item.get("page"))
    if page not in refs:
        if default_ref is None:
            raise ValueError("page")
        page = default_ref
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
