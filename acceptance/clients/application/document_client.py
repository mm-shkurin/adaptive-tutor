from uuid import uuid4

import httpx

from clients.application.http_result import HttpResult, read_result


class DocumentClient:
    def __init__(self, base_url: str):
        self.http = httpx.Client(base_url=base_url, timeout=300, follow_redirects=False)

    def submit_pdf(self, token: str, filename: str, content: bytes) -> HttpResult:
        return self.submit_upload(
            token,
            {"file": (filename, content, "application/pdf")},
        )

    def submit_no_file(self, token: str) -> HttpResult:
        response = self.http.post(
            "/api/v1/documents",
            headers={
                **self._bearer(token),
                "Idempotency-Key": str(uuid4()),
            },
        )
        return read_result(response)

    def submit_upload(self, token: str, files: dict, data: dict | None = None) -> HttpResult:
        request: dict = {
            "headers": {
                **self._bearer(token),
                "Idempotency-Key": str(uuid4()),
            },
            "files": files,
        }
        if data is not None:
            request["data"] = data
        response = self.http.post("/api/v1/documents", **request)
        return read_result(response)

    def submit_pdf_with_extra_fields(
        self, token: str, filename: str, content: bytes, fields: dict[str, str]
    ) -> HttpResult:
        return self.submit_upload(
            token,
            {"file": (filename, content, "application/pdf")},
            data=fields,
        )

    def read(self, token: str, document_id: str) -> HttpResult:
        response = self.http.get(f"/api/v1/documents/{document_id}", headers=self._bearer(token))
        return read_result(response)

    def read_as_guest(self, document_id: str) -> HttpResult:
        response = self.http.get(f"/api/v1/documents/{document_id}")
        return read_result(response)

    def list_as_guest(self, page: int = 1) -> HttpResult:
        response = self.http.get("/api/v1/documents", params={"page": page})
        return read_result(response)

    def submit_pdf_as_guest(self, filename: str, content: bytes) -> HttpResult:
        response = self.http.post(
            "/api/v1/documents",
            headers={"Idempotency-Key": str(uuid4())},
            files={"file": (filename, content, "application/pdf")},
        )
        return read_result(response)

    def list_documents(self, token: str, page: int = 1) -> HttpResult:
        response = self.http.get(
            "/api/v1/documents", headers=self._bearer(token), params={"page": page}
        )
        return read_result(response)

    def searchable_pieces(self, token: str, document_id: str) -> HttpResult:
        response = self.http.get(
            f"/acceptance/documents/{document_id}/searchable-pieces",
            headers=self._bearer(token),
        )
        return read_result(response)

    def move_indexing_status(self, token: str, document_id: str, status: str) -> HttpResult:
        response = self.http.post(
            f"/acceptance/documents/{document_id}/move",
            headers=self._bearer(token),
            json={"status": status},
        )
        return read_result(response)

    def close(self) -> None:
        self.http.close()

    def _bearer(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}
