from uuid import uuid4

import httpx

from clients.application.http_result import HttpResult, read_result


class DocumentClient:
    def __init__(self, base_url: str):
        self.http = httpx.Client(base_url=base_url, timeout=10, follow_redirects=False)

    def submit_pdf(self, token: str, filename: str, content: bytes) -> HttpResult:
        response = self.http.post(
            "/api/v1/documents",
            headers={
                "Authorization": f"Bearer {token}",
                "Idempotency-Key": str(uuid4()),
            },
            files={"file": (filename, content, "application/pdf")},
        )
        return read_result(response)

    def read(self, token: str, document_id: str) -> HttpResult:
        response = self.http.get(f"/api/v1/documents/{document_id}", headers=self._bearer(token))
        return read_result(response)

    def list_documents(self, token: str) -> HttpResult:
        response = self.http.get("/api/v1/documents", headers=self._bearer(token), params={"page": 1})
        return read_result(response)

    def close(self) -> None:
        self.http.close()

    def _bearer(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}
