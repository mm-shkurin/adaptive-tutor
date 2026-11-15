import httpx

from clients.application.http_result import HttpResult, read_result


class ChatClient:
    def __init__(self, base_url: str):
        self.http = httpx.Client(base_url=base_url, timeout=30, follow_redirects=False)

    def create(self, token: str, document_id: str) -> HttpResult:
        response = self.http.post(
            "/api/v1/chats",
            headers=self._bearer(token),
            json={"document_id": document_id},
        )
        return read_result(response)

    def list(self, token: str) -> HttpResult:
        response = self.http.get("/api/v1/chats", headers=self._bearer(token))
        return read_result(response)

    def send(self, token: str, chat_id: str, text: str, model: str, mode: str, key: str) -> HttpResult:
        response = self.http.post(
            f"/api/v1/chats/{chat_id}/messages",
            headers={**self._bearer(token), "Idempotency-Key": key},
            json={"text": text, "model": model, "mode": mode},
        )
        return read_result(response)

    def seed_search(self, token: str, document_id: str, pieces: tuple) -> HttpResult:
        response = self.http.post(
            f"/acceptance/documents/{document_id}/search-pieces",
            headers=self._bearer(token),
            json={"pieces": list(pieces)},
        )
        return read_result(response)

    def script_tutor(self, token: str, text: str) -> HttpResult:
        response = self.http.post(
            "/acceptance/tutor/script",
            headers=self._bearer(token),
            json={"text": text},
        )
        return read_result(response)

    def vectors(self, token: str, document_id: str) -> HttpResult:
        response = self.http.get(
            f"/acceptance/documents/{document_id}/vectors",
            headers=self._bearer(token),
        )
        return read_result(response)

    def tutor_calls(self, token: str) -> HttpResult:
        response = self.http.get("/acceptance/tutor/calls", headers=self._bearer(token))
        return read_result(response)

    def close(self) -> None:
        self.http.close()

    def _bearer(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}
