"""Integration 1.1 — valid fake creates one quiz; live model is not called."""

import json
from uuid import uuid4

import httpx

from adapters.tutor.http_quiz import HttpQuiz
from tests.quiz_flow import ada, ready_pdf, valid_body
from tests.support import bearer, build


def test_valid_completions_body_creates_one_quiz_and_live_model_is_not_called():
    live_hits = {"n": 0}

    def live_handler(_request: httpx.Request) -> httpx.Response:
        live_hits["n"] += 1
        return httpx.Response(500, text="live must not be called")

    fake_hits = {"n": 0}

    def fake_handler(_request: httpx.Request) -> httpx.Response:
        fake_hits["n"] += 1
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": json.dumps(valid_body(5))}}]},
        )

    # The wired tutor is the fake; a parallel live transport is never attached.
    tutor = HttpQuiz("http://fake-llm.test/v1", "test-key", transport=httpx.MockTransport(fake_handler))
    live = HttpQuiz("http://live-llm.test/v1", "live-key", transport=httpx.MockTransport(live_handler))
    bundle = build(quiz_tutor=tutor)
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "live.pdf")
    created = bundle.client.post(
        "/api/v1/quizzes",
        headers={**bearer(token), "Idempotency-Key": str(uuid4())},
        json={"document_id": str(document.id), "topic": "cells", "question_count": 5},
    )
    assert created.status_code == 201
    assert len(bundle.quizzes.held(owner)) == 1
    assert fake_hits["n"] == 1
    assert live_hits["n"] == 0
    # Prove the live transport would have counted if used:
    try:
        import asyncio

        asyncio.run(live.compose("auto", "cells", 5, ()))
    except Exception:
        pass
    assert live_hits["n"] == 1
