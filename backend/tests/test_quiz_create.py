import asyncio
from uuid import uuid4

import httpx
import pytest

from tests.quiz_flow import ada, hidden, listed, neighbour, post_quiz, ready_pdf, valid_body
from tests.support import bearer, build


@pytest.mark.parametrize("asked,stored", [(None, 5), (3, 3), (5, 5), (8, 8)])
def test_quiz_is_stored_from_the_selected_ready_pdf(asked, stored):
    bundle = build()
    token, owner = ada(bundle)
    older = ready_pdf(bundle, owner, "older.pdf")
    ready_pdf(bundle, owner, "newer.pdf", seed=False)
    key = str(uuid4())
    created = post_quiz(bundle, token, older.id, asked, topic=" cells ", key=key)
    assert created.status_code == 201
    body = created.json()
    replay = post_quiz(bundle, token, older.id, asked, topic=" cells ", key=key)
    assert replay.status_code == 201
    assert replay.json()["id"] == body["id"]
    assert len(bundle.quiz_tutor.calls) == 1
    call = bundle.quiz_tutor.calls[0]
    assert call.model == "auto"
    assert call.topic == "cells"
    assert call.count == stored
    assert len(call.pieces) <= 10
    assert {piece.page for piece in call.pieces} <= {2, 4}
    stored_quiz = bundle.quizzes.held(owner)
    assert len(stored_quiz) == 1
    assert stored_quiz[0].document_id == older.id
    assert len(stored_quiz[0].questions) == stored
    for question in stored_quiz[0].questions:
        assert len(question.choices) == 4
        assert sum(choice.id == question.correct_choice_id for choice in question.choices) == 1
        assert question.page in {2, 4}
    assert body["document_id"] == str(older.id)
    assert body["document_name"] == "older.pdf"
    assert body["topic"] == "cells"
    assert body["question_count"] == stored
    assert body["status"] == "take"
    assert body["current_index"] == 0
    assert body["last_score"] is None
    assert "slide" not in created.text
    assert len(body["questions"]) == stored
    for question in body["questions"]:
        hidden(question)
        assert len(question["choices"]) == 4
    grace_token, grace = neighbour(bundle)
    foreign = ready_pdf(bundle, grace, "grace.pdf")
    other = post_quiz(bundle, grace_token, foreign.id, 3)
    assert other.status_code == 201
    cards = listed(bundle, token).json()["quizzes"]
    assert cards[0]["id"] == body["id"]
    assert cards[0]["last_score"] is None
    assert cards[0]["document_name"] == "older.pdf"
    assert cards[0]["topic"] == "cells"
    assert cards[0]["question_count"] == stored
    assert "correct_choice_id" not in cards[0]
    assert other.json()["id"] not in {card["id"] for card in cards}


def test_the_same_key_stores_one_quiz_and_a_new_key_stores_another():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "older.pdf")
    key = str(uuid4())
    created = post_quiz(bundle, token, document.id, 5, topic="cells", key=key)
    assert created.status_code == 201
    quiz_id = created.json()["id"]
    assert len(bundle.quizzes.held(owner)) == 1
    assert len(bundle.quiz_tutor.calls) == 1
    replay = post_quiz(bundle, token, document.id, 5, topic="cells", key=key)
    assert replay.status_code == 201
    assert replay.json()["id"] == quiz_id
    assert len(bundle.quiz_tutor.calls) == 1
    assert [card["id"] for card in listed(bundle, token).json()["quizzes"]] == [quiz_id]
    other = post_quiz(bundle, token, document.id, 5, topic="cells", key=str(uuid4()))
    assert other.status_code == 201
    assert other.json()["id"] != quiz_id
    assert len(bundle.quizzes.held(owner)) == 2
    assert len(bundle.quiz_tutor.calls) == 2
    assert {card["id"] for card in listed(bundle, token).json()["quizzes"]} == {quiz_id, other.json()["id"]}


def test_two_creates_in_flight_with_the_same_attempt_store_one_quiz():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "older.pdf")
    bundle.quiz_tutor.script(valid_body(5))
    first, second = asyncio.run(_pair(bundle, token, document.id, str(uuid4())))
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    assert len(bundle.quizzes.held(owner)) == 1
    assert len(bundle.quiz_tutor.calls) == 1
    assert [card["id"] for card in listed(bundle, token).json()["quizzes"]] == [first.json()["id"]]


async def _pair(bundle, token, document_id, key):
    entered = asyncio.Event()
    release = asyncio.Event()
    bundle.quiz_tutor.hold(entered, release)
    transport = httpx.ASGITransport(app=bundle.client.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:

        async def once():
            return await client.post(
                "/api/v1/quizzes",
                headers={**bearer(token), "Idempotency-Key": key},
                json={"document_id": str(document_id), "topic": "cells", "question_count": 5},
            )

        async def gate():
            try:
                await asyncio.wait_for(entered.wait(), timeout=2)
                await asyncio.wait_for(_until(lambda: bundle.quizzes.waiting >= 1), timeout=2)
            finally:
                release.set()

        first, second, _ = await asyncio.gather(once(), once(), gate())
        return first, second


async def _until(ready):
    while not ready():
        await asyncio.sleep(0)


def test_missing_idempotency_key_stores_nothing():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "older.pdf")
    response = bundle.client.post(
        "/api/v1/quizzes",
        headers=bearer(token),
        json={"document_id": str(document.id), "topic": "cells", "question_count": 5},
    )
    assert response.status_code != 201
    assert bundle.quizzes.held(owner) == ()
    assert bundle.quiz_tutor.calls == []
