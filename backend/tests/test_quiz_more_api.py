"""Remaining Tier 2 API: session fail, examiner, language, unicode, last write."""

import asyncio
import unicodedata
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from domain.chat.chat import Chat
from domain.chat.choice import Choice
from tests.quiz_flow import ada, answer, listed, post_quiz, read, ready_pdf
from tests.support import bearer, build

MISSING = {"code": "quiz_not_found", "message": "Quiz was not found"}
STORE_DOWN = {"code": "unavailable", "message": "Quiz store is unavailable"}


def _world():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "gate.pdf")
    created = post_quiz(bundle, token, document.id, 3)
    assert created.status_code == 201
    quiz_id = created.json()["id"]
    choice_id = created.json()["questions"][0]["choices"][0]["id"]
    stored = bundle.quizzes.count()
    return bundle, token, document, quiz_id, choice_id, stored, owner


@pytest.mark.parametrize(
    "ask",
    ["list", "read", "create", "answer", "advance", "retry"],
)
def test_session_store_failure_is_refused_like_a_missing_quiz(ask):
    bundle, token, document, quiz_id, choice_id, stored, _owner = _world()
    bundle.store.dead = True
    if ask == "list":
        response = bundle.client.get("/api/v1/quizzes", headers=bearer(token))
    elif ask == "read":
        response = bundle.client.get(f"/api/v1/quizzes/{quiz_id}", headers=bearer(token))
    elif ask == "create":
        response = bundle.client.post(
            "/api/v1/quizzes",
            headers={**bearer(token), "Idempotency-Key": str(uuid4())},
            json={"document_id": str(document.id), "topic": "cells", "question_count": 5},
        )
    elif ask == "answer":
        response = answer(bundle, token, quiz_id, choice_id)
    elif ask == "advance":
        response = bundle.client.post(f"/api/v1/quizzes/{quiz_id}/advance", headers=bearer(token))
    else:
        response = bundle.client.post(f"/api/v1/quizzes/{quiz_id}/retries", headers=bearer(token))
    assert response.status_code == 404
    assert response.json() == MISSING
    assert bundle.quizzes.count() == stored


def test_examiner_series_does_not_appear_on_the_quiz_list():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "exam.pdf")
    chat = Chat.bound_to(document).with_vectors(True)
    choices = (
        Choice("c1", "one"),
        Choice("c2", "two"),
        Choice("c3", "three"),
        Choice("c4", "four"),
    )
    for index in range(3):
        chat, _ = chat.record_examiner_question(f"Q{index}", choices, "c1")
        chat, _ = chat.record_examiner_grade("c1", 2)
    assert chat.examiner_grade_count() == 3
    asyncio.run(bundle.chats.add(owner, chat, datetime.now(timezone.utc)))
    response = listed(bundle, token)
    assert response.status_code == 200
    assert response.json() == {"quizzes": []}
    assert bundle.quizzes.held(owner) == ()


@pytest.mark.parametrize(
    "topic,marker",
    [("митоз и клетки", "рус"), ("mitosis and cells", "eng")],
)
def test_questions_and_choices_follow_the_topics_language(topic, marker):
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "lang.pdf")
    payload = {
        "questions": [
            {
                "text": f"{marker} question {index}",
                "choices": [f"{marker} c{choice}" for choice in range(4)],
                "correct_index": 0,
                "page": 2,
            }
            for index in range(3)
        ]
    }
    bundle.quiz_tutor.script(payload)
    created = bundle.client.post(
        "/api/v1/quizzes",
        headers={**bearer(token), "Idempotency-Key": str(uuid4())},
        json={"document_id": str(document.id), "topic": topic, "question_count": 3},
    )
    assert created.status_code == 201
    assert bundle.quiz_tutor.calls[-1].topic == topic
    body = created.json()
    for question in body["questions"]:
        assert marker in question["text"]
        for choice in question["choices"]:
            assert marker in choice["text"]
    assert len(bundle.quizzes.held(owner)) == 1


def test_topic_questions_and_choices_round_trip_as_unicode():
    combining = "e\u0301"
    emoji = "🧬"
    base = "а" * (200 - len(unicodedata.normalize("NFC", combining + emoji)))
    raw_topic = f"  {base}{combining}{emoji}  "
    normalized = unicodedata.normalize("NFC", raw_topic).strip()
    assert len(normalized) == 200
    q_text = f"Q{combining}{emoji}"
    c_text = f"C{combining}{emoji}"
    payload = {
        "questions": [
            {
                "text": q_text,
                "choices": [c_text, "b", "c", "d"],
                "correct_index": 0,
                "page": 2,
            }
            for _ in range(3)
        ]
    }
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "uni.pdf")
    bundle.quiz_tutor.script(payload)
    created = bundle.client.post(
        "/api/v1/quizzes",
        headers={**bearer(token), "Idempotency-Key": str(uuid4())},
        json={"document_id": str(document.id), "topic": raw_topic, "question_count": 3},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["topic"] == normalized
    stored = bundle.quizzes.held(owner)[0]
    assert stored.topic == normalized
    expect_q = unicodedata.normalize("NFC", q_text)
    expect_c = unicodedata.normalize("NFC", c_text)
    assert stored.questions[0].text == expect_q
    assert stored.questions[0].choices[0].text == expect_c
    opened = read(bundle, token, body["id"]).json()
    assert opened["topic"] == normalized
    assert opened["questions"][0]["text"] == expect_q
    assert opened["questions"][0]["choices"][0]["text"] == expect_c


def test_failed_last_write_leaves_nothing_and_retry_stores_one():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "write.pdf")
    key = str(uuid4())
    bundle.quizzes.fail_next_add = True
    refused = post_quiz(bundle, token, document.id, 3, topic="cells", key=key)
    assert refused.status_code == 503
    assert refused.json() == STORE_DOWN
    assert bundle.quizzes.held(owner) == ()
    assert asyncio.run(bundle.quizzes.find_by_key(owner, key)) is None
    created = post_quiz(bundle, token, document.id, 3, topic="cells", key=key)
    assert created.status_code == 201
    assert len(bundle.quizzes.held(owner)) == 1
    assert asyncio.run(bundle.quizzes.find_by_key(owner, key)).id == UUID(created.json()["id"])
