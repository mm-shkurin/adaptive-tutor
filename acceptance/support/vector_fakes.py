import asyncio
import hashlib
import math
import socket
import threading
import time

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

DIMENSION = 384
MODEL = "all-MiniLM-L6-v2"


def embed_text(text: str) -> list[float]:
    vector = [0.0] * DIMENSION
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        vector[int.from_bytes(digest[:2], "big") % DIMENSION] += 1.0
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


class ExternalFakes:
    def __init__(self):
        self.points: dict[str, dict] = {}
        self.models: list[str] = []
        self.upserts: list[str] = []
        self._embed_fail: str | None = None
        self._lock = threading.Lock()
        port = _free_port()
        self.base_url = f"http://127.0.0.1:{port}"
        self.embeddings_url = self.base_url + "/v1"
        self.qdrant_url = self.base_url
        self._server = uvicorn.Server(
            uvicorn.Config(_app(self), host="127.0.0.1", port=port, log_level="warning", access_log=False)
        )
        self._thread = threading.Thread(target=self._server.run, daemon=True)

    def start(self) -> None:
        self._thread.start()
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try:
                response = httpx.get(self.base_url + "/health", timeout=0.5)
            except httpx.HTTPError:
                time.sleep(0.05)
                continue
            if response.status_code == 200:
                return
        raise RuntimeError("vector fakes did not become ready")

    def stop(self) -> None:
        self._server.should_exit = True
        self._thread.join(timeout=5)

    def fail_embeddings(self, mode: str | None) -> None:
        with self._lock:
            self._embed_fail = mode

    def clear_vectors(self, document_id: str) -> None:
        with self._lock:
            self.points = {
                key: point
                for key, point in self.points.items()
                if point["payload"]["document_id"] != document_id
            }

    def vectors_for(self, document_id: str) -> dict:
        with self._lock:
            points = [point for point in self.points.values() if point["payload"]["document_id"] == document_id]
            model = self.models[0] if self.models else ""
        points.sort(key=lambda point: point["payload"]["ordinal"])
        return {
            "model": model,
            "dimensions": [len(point["vector"]) for point in points],
            "pages": [point["payload"]["page"] for point in points],
            "texts": [point["payload"]["text"] for point in points],
        }

    def upsert_count(self, document_id: str) -> int:
        with self._lock:
            return sum(1 for item in self.upserts if item == document_id)


def _app(fakes: ExternalFakes) -> FastAPI:
    app = FastAPI()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/v1/embeddings")
    async def embeddings(request: Request):
        with fakes._lock:
            failure = fakes._embed_fail
        if failure == "times out":
            await asyncio.sleep(1.0)
            return Response(status_code=200)
        if failure == "returns a 4xx status":
            return JSONResponse(status_code=400, content={"error": "bad request"})
        if failure == "returns a 5xx status":
            return JSONResponse(status_code=500, content={"error": "server"})
        if failure == "returns a malformed body":
            return JSONResponse(status_code=200, content={"object": "list", "data": [{"index": 0}]})
        body = await request.json()
        if body.get("model") != MODEL:
            return JSONResponse(status_code=400, content={"error": "model"})
        raw = body.get("input", [])
        texts = [raw] if isinstance(raw, str) else list(raw)
        with fakes._lock:
            fakes.models.append(body["model"])
        data = [
            {"object": "embedding", "index": index, "embedding": embed_text(text)}
            for index, text in enumerate(texts)
        ]
        return {"object": "list", "data": data, "model": body["model"]}

    @app.put("/collections/{name}")
    def create_collection(name: str):
        return {"result": True, "status": "ok", "time": 0}

    @app.put("/collections/{name}/points")
    async def upsert(name: str, request: Request):
        body = await request.json()
        with fakes._lock:
            for point in body["points"]:
                fakes.points[str(point["id"])] = point
                fakes.upserts.append(point["payload"]["document_id"])
        return {"result": {"status": "completed"}, "status": "ok", "time": 0}

    @app.post("/collections/{name}/points/count")
    async def count(name: str, request: Request):
        body = await request.json()
        document_id = body["filter"]["must"][0]["match"]["value"]
        with fakes._lock:
            found = sum(1 for point in fakes.points.values() if point["payload"]["document_id"] == document_id)
        return {"result": {"count": found}, "status": "ok", "time": 0}

    @app.post("/collections/{name}/points/search")
    async def search(name: str, request: Request):
        body = await request.json()
        document_id = body["filter"]["must"][0]["match"]["value"]
        query = body["vector"]
        limit = int(body.get("limit", 10))
        with fakes._lock:
            found = [point for point in fakes.points.values() if point["payload"]["document_id"] == document_id]
        ranked = sorted(found, key=lambda point: _cosine(query, point["vector"]), reverse=True)
        return {
            "result": [
                {"id": point["id"], "score": _cosine(query, point["vector"]), "payload": point["payload"]}
                for point in ranked[:limit]
            ],
            "status": "ok",
            "time": 0,
        }

    return app


def _cosine(left, right) -> float:
    return sum(one * other for one, other in zip(left, right))


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]
