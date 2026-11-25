import json
from uuid import uuid4

import httpx
import pytest

from adapters.tutor.http_quiz import HttpQuiz
from tests.quiz_flow import ada, post_quiz, ready_pdf, valid_body
from tests.support import bearer, build
from usecase.chat.errors import ReplyFailed
from usecase.document.errors import StoreUnavailable

FAILED = {"code": "generation_failed", "message": "Quiz could not be assembled"}


@pytest.mark.parametrize("boom", [ReplyFailed, StoreUnavailable])
def test_a_failed_search_stores_nothing_and_does_not_call_the_model(boom):
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "older.pdf")
    bundle.search.fail(boom())
    response = post_quiz(bundle, token, document.id, 5)
    assert response.status_code == 400
    assert response.json() == FAILED
    assert bundle.quizzes.held(owner) == ()
    assert bundle.quiz_tutor.calls == []


@pytest.mark.parametrize("kind", ["timeout", "status-400", "status-500", "malformed"])
def test_a_failed_completions_call_stores_nothing_and_does_not_pin_the_attempt(kind):
    calls = {"n": 0}
    phase = {"fail": True}

    def handler(_request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if phase["fail"]:
            return _failure(kind)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": json.dumps(valid_body(5))}}]},
        )

    tutor = HttpQuiz("http://llm.test/v1", "key", transport=httpx.MockTransport(handler))
    bundle = build(quiz_tutor=tutor)
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "older.pdf")
    key = str(uuid4())
    refused = _create(bundle, token, document.id, key)
    assert refused.status_code == 400
    assert refused.json() == FAILED
    assert bundle.quizzes.held(owner) == ()
    first_calls = calls["n"]
    assert first_calls >= 1
    if kind in ("status-400", "status-500"):
        assert first_calls == 2
    else:
        assert first_calls == 1
    phase["fail"] = False
    created = _create(bundle, token, document.id, key)
    assert created.status_code == 201
    assert len(bundle.quizzes.held(owner)) == 1
    assert calls["n"] > first_calls


def _create(bundle, token, document_id, key):
    return bundle.client.post(
        "/api/v1/quizzes",
        headers={**bearer(token), "Idempotency-Key": key},
        json={"document_id": str(document_id), "topic": "cells", "question_count": 5},
    )


def _failure(kind: str) -> httpx.Response:
    if kind == "timeout":
        raise httpx.TimeoutException("timed out")
    if kind == "status-400":
        return httpx.Response(400, json={"error": "bad"})
    if kind == "status-500":
        return httpx.Response(500, text="down")
    return httpx.Response(200, json={"choices": [{"message": {"content": "not-json"}}]})
