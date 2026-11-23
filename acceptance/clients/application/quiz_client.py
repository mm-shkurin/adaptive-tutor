from __future__ import annotations

from uuid import uuid4

import httpx

from clients.application.http_result import HttpResult, read_result


class QuizClient:
    def __init__(self, base_url: str):
        self.http = httpx.Client(base_url=base_url, timeout=30, follow_redirects=False)

    def list(self, token: str) -> HttpResult:
        return read_result(self.http.get("/api/v1/quizzes", headers=self._bearer(token)))

    def get(self, token: str, quiz_id: str) -> HttpResult:
        return read_result(
            self.http.get(f"/api/v1/quizzes/{quiz_id}", headers=self._bearer(token))
        )

    def create(self, token: str, document_id: str, topic: str, count: int = 5, key: str | None = None) -> HttpResult:
        return read_result(
            self.http.post(
                "/api/v1/quizzes",
                headers={**self._bearer(token), "Idempotency-Key": key or str(uuid4())},
                json={"document_id": document_id, "topic": topic, "question_count": count},
            )
        )

    def answer(self, token: str, quiz_id: str, choice_id: str) -> HttpResult:
        return read_result(
            self.http.post(
                f"/api/v1/quizzes/{quiz_id}/answers",
                headers=self._bearer(token),
                json={"choice_id": choice_id},
            )
        )

    def advance(self, token: str, quiz_id: str) -> HttpResult:
        return read_result(
            self.http.post(f"/api/v1/quizzes/{quiz_id}/advance", headers=self._bearer(token))
        )

    def retry(self, token: str, quiz_id: str) -> HttpResult:
        return read_result(
            self.http.post(f"/api/v1/quizzes/{quiz_id}/retries", headers=self._bearer(token))
        )

    def script_tutor(self, token: str, payload: dict) -> HttpResult:
        response = self.http.post(
            "/acceptance/quiz-tutor/script",
            headers=self._bearer(token),
            json={"payload": payload},
        )
        return read_result(response)

    def seed_pieces(self, token: str, document_id: str, pieces: list[dict]) -> HttpResult:
        response = self.http.post(
            f"/acceptance/documents/{document_id}/search-pieces",
            headers=self._bearer(token),
            json={"pieces": pieces},
        )
        return read_result(response)

    @staticmethod
    def _bearer(token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}
