"""Tier 2 answer race, list cap, wipe-none, and length refusals."""

import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import httpx

from domain.chat.source import Source
from domain.quiz.attempt import Attempt
from domain.quiz.question import Question
from domain.quiz.quiz import Quiz
from tests.quiz_flow import ada, answer, hidden, listed, post_quiz, read, ready_pdf, valid_body
from tests.support import bearer, build
from usecase.quiz.ports import LIST_CAP
from usecase.quiz.wipe import QuizWipe

INVALID = {"code": "invalid_choice", "message": "Choice is not on the question"}
EMPTY_TOPIC = {"code": "empty_topic", "message": "Topic is empty"}
BAD_KEY = {"code": "invalid_idempotency_key", "message": "Idempotency key is not allowed"}


def _world():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "gate.pdf")
    created = post_quiz(bundle, token, document.id, 3)
    assert created.status_code == 201
    return bundle, token, created.json()["id"], owner


def test_list_returns_at_most_the_declared_cap():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "cap.pdf")
    pieces = (Source(page=2, text="alpha"),)
    built = Question.assemble(3, pieces, valid_body(3))
    start = datetime(2024, 5, 6, 7, 8, 9, tzinfo=timezone.utc)
    for index in range(LIST_CAP + 1):
        quiz = Quiz(
            id=uuid4(),
            document_id=document.id,
            document_name=document.name,
            topic=f"t{index}",
            questions=built,
            open_attempt=Attempt.start(),
            last_score=None,
        )
        asyncio.run(
            bundle.quizzes.add(owner, quiz, start + timedelta(seconds=index), str(uuid4()))
        )
    response = listed(bundle, token)
    assert response.status_code == 200
    cards = response.json()["quizzes"]
    assert len(cards) == LIST_CAP
    assert cards[0]["topic"] == f"t{LIST_CAP}"
    assert cards[-1]["topic"] == "t1"


def test_a_choice_that_is_not_on_the_question_is_refused():
    bundle, token, quiz_id, _owner = _world()
    refused = answer(bundle, token, quiz_id, str(uuid4()))
    assert refused.status_code == 400
    assert refused.json() == INVALID
    stayed = read(bundle, token, quiz_id).json()
    assert stayed["current_index"] == 0
    hidden(stayed["questions"][0])


def test_two_answers_at_the_same_moment_leave_one_grade():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "race.pdf")
    created = post_quiz(bundle, token, document.id, 3)
    assert created.status_code == 201
    quiz_id = created.json()["id"]
    first = created.json()["questions"][0]["choices"][0]["id"]
    second = created.json()["questions"][0]["choices"][1]["id"]
    left, right = asyncio.run(_pair_answers(bundle, token, quiz_id, first, second))
    assert left.status_code == 200
    assert right.status_code == 200
    left_grade = left.json()["questions"][0]
    right_grade = right.json()["questions"][0]
    assert left_grade["chosen_choice_id"] == right_grade["chosen_choice_id"]
    assert left_grade["correct"] == right_grade["correct"]
    assert left_grade["correct_choice_id"] == right_grade["correct_choice_id"]
    stored = bundle.quizzes.held(owner)[0]
    assert len(stored.open_attempt.answers) == 1


def test_wipe_with_no_account_removes_nothing():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "keep.pdf")
    created = post_quiz(bundle, token, document.id, 3)
    assert created.status_code == 201
    before = bundle.quizzes.count()
    asyncio.run(QuizWipe(bundle.quizzes).wipe(None))
    assert bundle.quizzes.count() == before
    assert len(bundle.quizzes.held(owner)) == 1


def test_topic_past_the_maximum_is_refused():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "long.pdf")
    response = post_quiz(bundle, token, document.id, 5, topic="x" * 201)
    assert response.status_code == 400
    assert response.json() == EMPTY_TOPIC
    assert bundle.quizzes.held(owner) == ()
    assert bundle.quiz_tutor.calls == []


def test_idempotency_key_past_the_maximum_is_refused():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "key.pdf")
    response = bundle.client.post(
        "/api/v1/quizzes",
        headers={**bearer(token), "Idempotency-Key": "k" * 129},
        json={"document_id": str(document.id), "topic": "cells", "question_count": 5},
    )
    assert response.status_code == 400
    assert response.json() == BAD_KEY
    assert bundle.quizzes.held(owner) == ()
    assert bundle.quiz_tutor.calls == []


def test_empty_idempotency_key_is_refused():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "empty-key.pdf")
    response = bundle.client.post(
        "/api/v1/quizzes",
        headers={**bearer(token), "Idempotency-Key": ""},
        json={"document_id": str(document.id), "topic": "cells", "question_count": 5},
    )
    assert response.status_code == 400
    assert response.json() == BAD_KEY
    assert bundle.quizzes.held(owner) == ()
    assert bundle.quiz_tutor.calls == []


async def _pair_answers(bundle, token, quiz_id, first, second):
    transport = httpx.ASGITransport(app=bundle.client.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:

        async def once(choice_id):
            return await client.post(
                f"/api/v1/quizzes/{quiz_id}/answers",
                headers=bearer(token),
                json={"choice_id": choice_id},
            )

        return await asyncio.gather(once(first), once(second))
