from uuid import uuid4

import pytest

from tests.quiz_flow import ada, advance, answer, listed, post_quiz, read, ready_pdf, retry, unready_pdf
from tests.support import build

MISSING = {"code": "quiz_not_found", "message": "Quiz was not found"}
NOT_READY = {"code": "document_not_ready", "message": "Document is not ready"}
NO_READY = {"code": "no_ready_document", "message": "No ready document"}


def _world():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "gate.pdf")
    created = post_quiz(bundle, token, document.id, 3)
    assert created.status_code == 201
    quiz_id = created.json()["id"]
    choice_id = created.json()["questions"][0]["choices"][0]["id"]
    stored = bundle.quizzes.count()
    return bundle, document, quiz_id, choice_id, stored


@pytest.mark.parametrize(
    "ask",
    ["list", "read", "create", "answer", "advance", "retry"],
)
def test_a_call_with_no_session_is_refused_like_a_missing_quiz(ask):
    bundle, document, quiz_id, choice_id, stored = _world()
    if ask == "list":
        response = bundle.client.get("/api/v1/quizzes")
    elif ask == "read":
        response = bundle.client.get(f"/api/v1/quizzes/{quiz_id}")
    elif ask == "create":
        response = bundle.client.post(
            "/api/v1/quizzes",
            headers={"Idempotency-Key": str(uuid4())},
            json={"document_id": str(document.id), "topic": "cells", "question_count": 5},
        )
    elif ask == "answer":
        response = bundle.client.post(
            f"/api/v1/quizzes/{quiz_id}/answers",
            json={"choice_id": choice_id},
        )
    elif ask == "advance":
        response = bundle.client.post(f"/api/v1/quizzes/{quiz_id}/advance")
    else:
        response = bundle.client.post(f"/api/v1/quizzes/{quiz_id}/retries")
    assert response.status_code == 404
    assert response.json() == MISSING
    assert bundle.quizzes.count() == stored


@pytest.mark.parametrize(
    "state",
    ["waiting", "indexing", "failed", "a status that is not a known document status"],
)
def test_a_document_that_is_not_ready_cannot_start_a_quiz(state):
    bundle = build()
    token, owner = ada(bundle)
    ready_pdf(bundle, owner, "ready.pdf")
    document = unready_pdf(bundle, owner, f"{state}.pdf", state)
    before = bundle.client.get(f"/api/v1/documents/{document.id}", headers={"Authorization": f"Bearer {token}"})
    assert before.status_code == 200
    response = post_quiz(bundle, token, document.id, 5, topic="cells")
    assert response.status_code == 400
    assert response.json() == NOT_READY
    assert bundle.quizzes.held(owner) == ()
    assert bundle.quiz_tutor.calls == []
    after = bundle.client.get(f"/api/v1/documents/{document.id}", headers={"Authorization": f"Bearer {token}"})
    assert after.status_code == 200
    assert after.json()["status"] == before.json()["status"]


def test_a_person_with_no_ready_pdf_cannot_start_a_quiz():
    bundle = build()
    token, owner = ada(bundle)
    waiting = unready_pdf(bundle, owner, "waiting.pdf", "waiting")
    response = post_quiz(bundle, token, waiting.id, 5, topic="cells")
    assert response.status_code == 400
    assert response.json() == NO_READY
    assert listed(bundle, token).json() == {"quizzes": []}
    assert bundle.quizzes.held(owner) == ()
    assert bundle.quiz_tutor.calls == []