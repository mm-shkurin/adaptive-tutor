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

    def close(self) -> None:
        self.http.close()

    def _bearer(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}
