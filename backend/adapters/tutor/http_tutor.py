import httpx

from domain.chat.source import Source
from usecase.chat.errors import ReplyFailed

_LANGUAGE = (
    "Always reply in the same language as the Question. "
    "If the question is Russian, the whole answer must be Russian — never English."
)

_MODE_SYSTEM = {
    "professor": (
        "You are a professor. Answer only from the supplied material. "
        "Use an academic tone. Do not invent facts outside the material. "
        f"{_LANGUAGE}"
    ),
    "five_year_old": (
        "Explain only from the supplied material in plain words a five-year-old "
        "would understand. Do not invent facts outside the material. "
        f"{_LANGUAGE}"
    ),
    "socratic": (
        "Ask one short guiding question grounded only in the supplied material. "
        "Do not give the answer. "
        f"{_LANGUAGE}"
    ),
    "examiner": (
        "Write one exam question grounded only in the supplied material. "
        "Do not include answer choices. "
        f"{_LANGUAGE}"
    ),
}


class HttpTutor:
    def __init__(self, base_url: str, api_key: str, timeout: float = 5, transport=None):
        self._url = base_url.rstrip("/") + "/chat/completions"
        self._api_key = api_key
        self._timeout = timeout
        self._transport = transport
        self.live = 0

    async def answer(self, model: str, mode: str, question: str, sources: tuple[Source, ...]) -> str:
        if not self._api_key:
            raise ReplyFailed()
        self.live += 1
        try:
            return await self._completion(model, mode, question, sources)
        finally:
            self.live -= 1

    async def _completion(
        self, model: str, mode: str, question: str, sources: tuple[Source, ...]
    ) -> str:
        try:
            response = await self._posted_or_auto(model, mode, question, sources)
            return _assistant_text(response.json())
        except (KeyError, TypeError, ValueError, IndexError) as error:
            raise ReplyFailed() from error

    async def _posted_or_auto(
        self, model: str, mode: str, question: str, sources: tuple[Source, ...]
    ) -> httpx.Response:
        response = await self._post(model, mode, question, sources)
        if not _http_ok(response) and model != "auto":
            response = await self._post("auto", mode, question, sources)
        if not _http_ok(response):
            raise ReplyFailed()
        return response

    async def _post(
        self, model: str, mode: str, question: str, sources: tuple[Source, ...]
    ) -> httpx.Response:
        try:
            return await self._request(_completion_body(model, mode, question, sources))
        except httpx.HTTPError as error:
            raise ReplyFailed() from error

    async def _request(self, body: dict) -> httpx.Response:
        async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
            return await client.post(
                self._url, headers=_auth_headers(self._api_key), json=body
            )


def _http_ok(response: httpx.Response) -> bool:
    return 200 <= response.status_code < 300


def _auth_headers(api_key: str) -> dict[str, str]:
    return {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}


def _completion_body(
    model: str, mode: str, question: str, sources: tuple[Source, ...]
) -> dict:
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": _MODE_SYSTEM.get(mode, _MODE_SYSTEM["professor"])},
            {"role": "user", "content": _user_content(question, sources)},
        ],
    }


def _user_content(question: str, sources: tuple[Source, ...]) -> str:
    return (
        f"Material:\n{_material(sources)}\n\n"
        f"Question:\n{question}\n\n"
        "Reply in the same language as the Question."
    )


def _material(sources: tuple[Source, ...]) -> str:
    if not sources:
        return "(no material)"
    return "\n".join(_source_line(source) for source in sources)


def _source_line(source: Source) -> str:
    page = f"page {source.page}" if source.page is not None else "no page"
    return f"[{page}] {source.text}"


def _assistant_text(body: object) -> str:
    if not isinstance(body, dict):
        raise ValueError("body")
    content = body["choices"][0]["message"]["content"]
    if not isinstance(content, str) or content.strip() == "":
        raise ValueError("empty")
    return content
