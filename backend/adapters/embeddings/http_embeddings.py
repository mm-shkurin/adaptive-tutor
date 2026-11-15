import httpx

from usecase.document.errors import StoreUnavailable

MODEL = "all-MiniLM-L6-v2"
DIMENSION = 384


class HttpEmbeddings:
    def __init__(self, base_url: str, api_key: str):
        self._url = base_url.rstrip("/") + "/embeddings"
        self._api_key = api_key

    async def embed(self, texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
        response = await self._post(texts)
        if response.status_code != 200:
            raise StoreUnavailable()
        return _vectors(response.json(), len(texts))

    async def _post(self, texts: tuple[str, ...]) -> httpx.Response:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        async with httpx.AsyncClient(timeout=10) as client:
            return await client.post(self._url, headers=headers, json={"model": MODEL, "input": list(texts)})


def _vectors(body: dict, count: int) -> tuple[tuple[float, ...], ...]:
    ordered = sorted(body["data"], key=lambda item: item["index"])
    vectors = tuple(tuple(item["embedding"]) for item in ordered)
    if len(vectors) != count or any(len(vector) != DIMENSION for vector in vectors):
        raise StoreUnavailable()
    return vectors
