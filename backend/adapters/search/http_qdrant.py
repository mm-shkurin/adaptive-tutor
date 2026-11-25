from uuid import UUID, uuid5, NAMESPACE_URL

import httpx

from domain.document.placed_text import PlacedPiece
from usecase.document.errors import StoreUnavailable

COLLECTION = "document_pieces"


class HttpQdrant:
    def __init__(self, base_url: str, api_key: str):
        self._base = base_url.rstrip("/")
        self._api_key = api_key
        self._ensured = False

    async def upsert(
        self,
        document_id: UUID,
        pieces: tuple[tuple[int, PlacedPiece], ...],
        vectors: tuple[tuple[float, ...], ...],
    ) -> None:
        await self._ensure()
        await self._ok(
            "PUT",
            f"/collections/{COLLECTION}/points?wait=true",
            {
                "points": [
                    _point(document_id, ordinal, piece, vector)
                    for (ordinal, piece), vector in zip(pieces, vectors)
                ]
            },
        )

    async def count(self, document_id: UUID) -> int:
        try:
            body = await self._ok(
                "POST",
                f"/collections/{COLLECTION}/points/count",
                {"exact": True, "filter": _filter(document_id)},
            )
        except StoreUnavailable:
            return 0
        return int(body["result"]["count"])

    async def ordinals(self, document_id: UUID) -> frozenset[int]:
        try:
            body = await self._ok(
                "POST",
                f"/collections/{COLLECTION}/points/scroll",
                {
                    "filter": _filter(document_id),
                    "limit": 10000,
                    "with_payload": True,
                    "with_vector": False,
                },
            )
        except StoreUnavailable:
            return frozenset()
        points = body["result"]["points"]
        return frozenset(int(point["payload"]["ordinal"]) for point in points)

    async def search(self, document_id: UUID, vector: tuple[float, ...], limit: int) -> list:
        body = await self._ok(
            "POST",
            f"/collections/{COLLECTION}/points/search",
            {"vector": list(vector), "limit": limit, "with_payload": True, "filter": _filter(document_id)},
        )
        return body["result"]

    async def _ensure(self) -> None:
        if self._ensured:
            return
        response = await self._send("PUT", f"/collections/{COLLECTION}", {"vectors": {"size": 384, "distance": "Cosine"}})
        if response.status_code not in {200, 409}:
            raise StoreUnavailable()
        self._ensured = True

    async def _ok(self, method: str, path: str, payload: dict) -> dict:
        response = await self._send(method, path, payload)
        if response.status_code != 200:
            raise StoreUnavailable()
        return response.json()

    async def _send(self, method: str, path: str, payload: dict) -> httpx.Response:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["api-key"] = self._api_key
        async with httpx.AsyncClient(timeout=60) as client:
            return await client.request(method, self._base + path, headers=headers, json=payload)


def _point(document_id: UUID, ordinal: int, piece: PlacedPiece, vector: tuple[float, ...]) -> dict:
    return {
        "id": str(uuid5(NAMESPACE_URL, f"{document_id}:{ordinal}")),
        "vector": list(vector),
        "payload": {
            "document_id": str(document_id),
            "ordinal": ordinal,
            "text": piece.text,
            "page": piece.page,
            "slide": piece.slide,
        },
    }


def _filter(document_id: UUID) -> dict:
    return {"must": [{"key": "document_id", "match": {"value": str(document_id)}}]}
