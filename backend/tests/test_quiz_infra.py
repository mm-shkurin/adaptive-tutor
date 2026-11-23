"""Tier 2 infrastructure scenarios for quizzes."""

import asyncio
from datetime import datetime, timezone
from uuid import uuid4

import httpx
import pytest

from adapters.tutor.http_quiz import HttpQuiz
from domain.chat.source import Source
from domain.quiz.attempt import Attempt
from domain.quiz.question import Question
from domain.quiz.quiz import Quiz
from tests.quiz_flow import (
    ada,
    advance,
    answer,
    listed,
    neighbour,
    post_quiz,
    read,
    ready_pdf,
    retry,
    valid_body,
)
from tests.support import bearer, build

STORE_DOWN = {"code": "unavailable", "message": "Quiz store is unavailable"}
FAILED = {"code": "generation_failed", "message": "Quiz could not be assembled"}


def test_dead_quiz_store_refuses_a_read():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "dead.pdf")
    created = post_quiz(bundle, token, document.id, 3)
    assert created.status_code == 201
    quiz_id = created.json()["id"]
    before = listed(bundle, token).json()
    bundle.quizzes.dead = True
    for response in (listed(bundle, token), read(bundle, token, quiz_id)):
        assert response.status_code == 503
        assert response.json() == STORE_DOWN
        assert "topic" not in response.text
    assert bundle.quizzes.live == 0
    bundle.quizzes.dead = False
    restored = listed(bundle, token)
    assert restored.status_code == 200
    assert restored.json() == before


@pytest.mark.parametrize("write", ["create", "answer", "advance", "retry"])
def test_dead_quiz_store_refuses_a_write_and_stores_nothing(write):
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "write.pdf")
    created = post_quiz(bundle, token, document.id, 3)
    assert created.status_code == 201
    quiz_id = created.json()["id"]
    choice_id = created.json()["questions"][0]["choices"][0]["id"]
    if write == "advance":
        assert answer(bundle, token, quiz_id, choice_id).status_code == 200
    stored = bundle.quizzes.count()
    calls = len(bundle.quiz_tutor.calls)
    bundle.quizzes.dead = True
    if write == "create":
        response = post_quiz(bundle, token, document.id, 3, topic="other")
    elif write == "answer":
        response = answer(bundle, token, quiz_id, choice_id)
    elif write == "advance":
        response = advance(bundle, token, quiz_id)
    else:
        response = retry(bundle, token, quiz_id)
    assert response.status_code == 503
    assert response.json() == STORE_DOWN
    assert bundle.quizzes.count() == stored
    assert len(bundle.quiz_tutor.calls) == calls
    assert bundle.quizzes.live == 0


def test_list_and_create_work_after_the_store_recovers():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "recover.pdf")
    created = post_quiz(bundle, token, document.id, 3, topic="before")
    assert created.status_code == 201
    before = listed(bundle, token).json()
    bundle.quizzes.dead = True
    assert listed(bundle, token).status_code == 503
    assert post_quiz(bundle, token, document.id, 3, topic="during").status_code == 503
    bundle.quizzes.dead = False
    restored = listed(bundle, token)
    assert restored.status_code == 200
    assert restored.json() == before
    again = post_quiz(bundle, token, document.id, 3, topic="after")
    assert again.status_code == 201
    assert len(bundle.quizzes.held(owner)) == 2


def test_repeated_failed_creates_return_connections_to_baseline():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "leak.pdf")
    baseline = bundle.quizzes.live
    bundle.quizzes.dead = True
    for _ in range(5):
        assert post_quiz(bundle, token, document.id, 3).status_code == 503
    assert bundle.quizzes.live == baseline
    bundle.quizzes.dead = False
    bundle.quiz_tutor.fail()
    for _ in range(5):
        refused = bundle.client.post(
            "/api/v1/quizzes",
            headers={**bearer(token), "Idempotency-Key": str(uuid4())},
            json={"document_id": str(document.id), "topic": "cells", "question_count": 3},
        )
        assert refused.status_code == 400
    assert bundle.quizzes.live == baseline
    bundle.quiz_tutor.script(valid_body(3))
    created = post_quiz(bundle, token, document.id, 3)
    assert created.status_code == 201
    assert len(bundle.quizzes.held(owner)) == 1


def test_missing_model_key_does_not_stop_startup():
    tutor = HttpQuiz("http://llm.test/v1", "")
    bundle = build(quiz_tutor=tutor)
    assert bundle.client.get("/api/v1/auth/oauth/yandex/start", follow_redirects=False).status_code in {
        302,
        307,
    }


def test_missing_model_key_fails_create_and_stores_nothing():
    tutor = HttpQuiz("http://llm.test/v1", "")
    bundle = build(quiz_tutor=tutor)
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "nokey.pdf")
    response = bundle.client.post(
        "/api/v1/quizzes",
        headers={**bearer(token), "Idempotency-Key": str(uuid4())},
        json={"document_id": str(document.id), "topic": "cells", "question_count": 5},
    )
    assert response.status_code == 400
    assert response.json() == FAILED
    assert bundle.quizzes.held(owner) == ()
    text = response.text
    assert "Traceback" not in text
    assert "/Users/" not in text


def test_failure_body_omits_secret_document_text_and_neighbour_quiz():
    secret = "sk-live-quiz-secret-value"
    sentence = "UNIQUE_DOCUMENT_SENTENCE_ALPHA"
    neighbour_topic = "NEIGHBOUR_QUIZ_TOPIC_UNIQUE"

    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timed out")

    tutor = HttpQuiz("http://llm.test/v1", secret, transport=httpx.MockTransport(handler))
    bundle = build(quiz_tutor=tutor)
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "redact.pdf", seed=False)
    bundle.search.seed(document.id, (Source(page=2, text=sentence),))
    _grace_token, grace = neighbour(bundle)
    foreign = ready_pdf(bundle, grace, "grace.pdf")
    pieces = (Source(page=2, text="alpha"),)
    built = Question.assemble(3, pieces, valid_body(3))
    neighbour_quiz = Quiz(
        id=uuid4(),
        document_id=foreign.id,
        document_name=foreign.name,
        topic=neighbour_topic,
        questions=built,
        open_attempt=Attempt.start(),
        last_score=None,
    )
    asyncio.run(
        bundle.quizzes.add(grace, neighbour_quiz, datetime.now(timezone.utc), str(uuid4()))
    )
    response = bundle.client.post(
        "/api/v1/quizzes",
        headers={**bearer(token), "Idempotency-Key": str(uuid4())},
        json={"document_id": str(document.id), "topic": "cells", "question_count": 5},
    )
    assert response.status_code == 400
    assert response.json() == FAILED
    assert bundle.quizzes.held(owner) == ()
    body = response.text
    assert secret not in body
    assert sentence not in body
    assert neighbour_topic not in body
    assert "Traceback" not in body
    assert "StoreUnavailable" not in body
    assert "HttpQuiz" not in body
