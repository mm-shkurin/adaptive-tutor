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

    def open(self, token: str, document_id: str) -> HttpResult:
        response = self.http.post(
            "/api/v1/chats/open",
            headers=self._bearer(token),
            json={"document_id": document_id},
        )
        return read_result(response)

    def get(self, token: str, chat_id: str) -> HttpResult:
        response = self.http.get(f"/api/v1/chats/{chat_id}", headers=self._bearer(token))
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

    def fail_tutor(self, token: str) -> HttpResult:
        response = self.http.post(
            "/acceptance/tutor/fail",
            headers=self._bearer(token),
        )
        return read_result(response)

    def hang_tutor(self, token: str) -> HttpResult:
        response = self.http.post(
            "/acceptance/tutor/hang",
            headers=self._bearer(token),
        )
        return read_result(response)

    def advance_on_match(self, token: str, offset_ms: int) -> HttpResult:
        response = self.http.post(
            "/acceptance/search/advance-on-match",
            headers=self._bearer(token),
            json={"offset_ms": offset_ms},
        )
        return read_result(response)

    def arm_vector_interleave(self, token: str) -> HttpResult:
        response = self.http.post(
            "/acceptance/vectors/interleave",
            headers=self._bearer(token),
        )
        return read_result(response)

    def interleave_open(self, token: str, chat_id: str) -> HttpResult:
        response = self.http.post(
            f"/acceptance/chats/{chat_id}/interleave-open",
            headers=self._bearer(token),
        )
        return read_result(response)

    def write_empty_vectors(self, token: str) -> HttpResult:
        response = self.http.post(
            "/acceptance/vectors/write-empty",
            headers=self._bearer(token),
        )
        return read_result(response)

    def vectors(self, token: str, document_id: str) -> HttpResult:
        response = self.http.get(
            f"/acceptance/documents/{document_id}/vectors",
            headers=self._bearer(token),
        )
        return read_result(response)

    def vector_failure(self, token: str, document_id: str) -> HttpResult:
        response = self.http.get(
            f"/acceptance/documents/{document_id}/vector-failure",
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
