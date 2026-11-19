from __future__ import annotations

import httpx

from clients.application.http_result import HttpResult, read_result


class ChatClient:
    def __init__(self, base_url: str):
        self.http = httpx.Client(base_url=base_url, timeout=30, follow_redirects=False)

    def create(self, token: str, document_id: str) -> HttpResult:
        return self.create_payload(token, {"document_id": document_id})

    def create_without_document(self, token: str) -> HttpResult:
        return self.create_payload(token, {})

    def create_payload(self, token: str, payload: dict) -> HttpResult:
        response = self.http.post(
            "/api/v1/chats",
            headers=self._bearer(token),
            json=payload,
        )
        return read_result(response)

    def open(self, token: str, document_id: str) -> HttpResult:
        return self.open_payload(token, {"document_id": document_id})

    def open_payload(self, token: str, payload: dict) -> HttpResult:
        response = self.http.post(
            "/api/v1/chats/open",
            headers=self._bearer(token),
            json=payload,
        )
        return read_result(response)

    def get(self, token: str, chat_id: str) -> HttpResult:
        response = self.http.get(f"/api/v1/chats/{chat_id}", headers=self._bearer(token))
        return read_result(response)

    def list(self, token: str) -> HttpResult:
        response = self.http.get("/api/v1/chats", headers=self._bearer(token))
        return read_result(response)

    def send(self, token: str, chat_id: str, text: str, model: str, mode: str, key: str) -> HttpResult:
        return self.send_payload(
            token, chat_id, {"text": text, "model": model, "mode": mode}, key
        )

    def send_payload(self, token: str | None, chat_id: str, payload: dict, key: str) -> HttpResult:
        headers = {"Idempotency-Key": key}
        if token is not None:
            headers = {**self._bearer(token), **headers}
        response = self.http.post(
            f"/api/v1/chats/{chat_id}/messages",
            headers=headers,
            json=payload,
        )
        return read_result(response)

    def list_without_session(self) -> HttpResult:
        return read_result(self.http.get("/api/v1/chats"))

    def get_without_session(self, chat_id: str) -> HttpResult:
        return read_result(self.http.get(f"/api/v1/chats/{chat_id}"))

    def create_without_session(self, document_id: str | None = None) -> HttpResult:
        body = {} if document_id is None else {"document_id": document_id}
        return read_result(self.http.post("/api/v1/chats", json=body))

    def open_without_session(self, document_id: str) -> HttpResult:
        return read_result(
            self.http.post("/api/v1/chats/open", json={"document_id": document_id})
        )

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

    def fail_search(self, token: str) -> HttpResult:
        response = self.http.post(
            "/acceptance/search/fail",
            headers=self._bearer(token),
        )
        return read_result(response)

    def clear_model_key(self, token: str) -> HttpResult:
        response = self.http.post(
            "/acceptance/model-key/clear",
            headers=self._bearer(token),
        )
        return read_result(response)

    def set_model_key(self, token: str, key: str) -> HttpResult:
        response = self.http.post(
            "/acceptance/model-key/set",
            headers=self._bearer(token),
            json={"key": key},
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

    def hold_tutor(self, token: str) -> HttpResult:
        response = self.http.post(
            "/acceptance/tutor/hold",
            headers=self._bearer(token),
        )
        return read_result(response)

    def reply_after_switch(
        self,
        token: str,
        chat_id: str,
        document_id: str,
        text: str,
        model: str,
        mode: str,
        key: str,
    ) -> HttpResult:
        response = self.http.post(
            f"/acceptance/chats/{chat_id}/reply-after-switch",
            headers=self._bearer(token),
            json={
                "document_id": document_id,
                "text": text,
                "model": model,
                "mode": mode,
                "key": key,
            },
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

    def reset_store_reads(self, token: str) -> HttpResult:
        response = self.http.post(
            "/acceptance/chats/store-reads/reset",
            headers=self._bearer(token),
        )
        return read_result(response)

    def store_reads(self, token: str) -> HttpResult:
        response = self.http.get(
            "/acceptance/chats/store-reads",
            headers=self._bearer(token),
        )
        return read_result(response)

    def fail_session_store(self, token: str) -> HttpResult:
        response = self.http.post(
            "/acceptance/session-store/fail",
            headers=self._bearer(token),
        )
        return read_result(response)

    def recover_session_store(self) -> HttpResult:
        response = self.http.post("/acceptance/session-store/recover")
        return read_result(response)

    def fail_chat_store(self, token: str) -> HttpResult:
        response = self.http.post(
            "/acceptance/chat-store/fail",
            headers=self._bearer(token),
        )
        return read_result(response)

    def recover_chat_store(self) -> HttpResult:
        response = self.http.post("/acceptance/chat-store/recover")
        return read_result(response)

    def arm_thread_interleave(self, token: str) -> HttpResult:
        response = self.http.post(
            "/acceptance/chats/interleave-thread",
            headers=self._bearer(token),
        )
        return read_result(response)

    def arm_attempt_interleave(self, token: str) -> HttpResult:
        response = self.http.post(
            "/acceptance/chats/interleave-attempt",
            headers=self._bearer(token),
        )
        return read_result(response)

    def interleave_sends(self, token: str, chat_id: str, attempts: list[dict]) -> HttpResult:
        response = self.http.post(
            f"/acceptance/chats/{chat_id}/interleave-sends",
            headers=self._bearer(token),
            json={"attempts": attempts},
        )
        return read_result(response)

    def close(self) -> None:
        self.http.close()

    def _bearer(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}
