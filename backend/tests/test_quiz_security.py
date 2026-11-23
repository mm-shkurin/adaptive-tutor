"""Tier 2 security scenarios for quizzes."""

from uuid import uuid4

from domain.chat.source import Source
from tests.quiz_flow import ada, listed, neighbour, post_quiz, ready_pdf
from tests.support import bearer, build

SCRIPT = "<script>alert(1)</script>"
SQL = "' OR 1=1"


def test_script_and_sql_fragment_round_trip_as_text():
    payload = {
        "questions": [
            {
                "text": f"Q {SCRIPT} {SQL}",
                "choices": [f"A {SCRIPT}", f"B {SQL}", "C", "D"],
                "correct_index": 0,
                "page": 2,
            }
            for _ in range(3)
        ]
    }
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "xss.pdf", seed=False)
    bundle.search.seed(document.id, (Source(page=2, text=f"piece {SCRIPT} {SQL}"),))
    topic = f"topic {SCRIPT} {SQL}"
    bundle.quiz_tutor.script(payload)
    created = bundle.client.post(
        "/api/v1/quizzes",
        headers={**bearer(token), "Idempotency-Key": str(uuid4())},
        json={"document_id": str(document.id), "topic": topic, "question_count": 3},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["topic"] == topic
    assert SCRIPT in body["questions"][0]["text"]
    assert SQL in body["questions"][0]["text"]
    assert SCRIPT in body["questions"][0]["choices"][0]["text"]
    assert SQL in body["questions"][0]["choices"][1]["text"]
    cards = listed(bundle, token).json()["quizzes"]
    assert len(cards) == 1
    assert cards[0]["topic"] == topic
    grace_token, grace = neighbour(bundle)
    foreign = ready_pdf(bundle, grace, "grace.pdf")
    other = post_quiz(bundle, grace_token, foreign.id, 3, topic="neighbour")
    assert other.status_code == 201
    again = listed(bundle, token)
    assert [card["id"] for card in again.json()["quizzes"]] == [body["id"]]
    assert "neighbour" not in again.text


def test_server_owned_fields_on_create_are_ignored():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "mass.pdf")
    bundle.quiz_tutor.script(
        {
            "questions": [
                {
                    "text": f"Question {index}",
                    "choices": [f"q{index}c{choice}" for choice in range(4)],
                    "correct_index": 0,
                    "page": 2,
                }
                for index in range(3)
            ]
        }
    )
    forged_id = str(uuid4())
    created = bundle.client.post(
        "/api/v1/quizzes",
        headers={**bearer(token), "Idempotency-Key": str(uuid4())},
        json={
            "document_id": str(document.id),
            "topic": "cells",
            "question_count": 3,
            "id": forged_id,
            "owner_id": str(uuid4()),
            "status": "result",
            "last_score": {"correct": 3, "total": 3},
            "correct_choice_id": "forged",
            "created_at": "1999-01-01T00:00:00Z",
            "role": "admin",
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["id"] != forged_id
    assert body["status"] == "take"
    assert body["last_score"] is None
    assert body["current_index"] == 0
    stored = bundle.quizzes.held(owner)[0]
    assert str(stored.id) == body["id"]
    assert listed(bundle, token).json()["quizzes"][0]["last_score"] is None
    assert "role" not in body
    assert "created_at" not in body


def test_server_owned_fields_on_an_answer_are_ignored():
    bundle = build()
    token, _owner = ada(bundle)
    document = ready_pdf(bundle, _owner, "ans.pdf")
    created = post_quiz(bundle, token, document.id, 3)
    assert created.status_code == 201
    quiz_id = created.json()["id"]
    wrong = created.json()["questions"][0]["choices"][1]["id"]
    graded = bundle.client.post(
        f"/api/v1/quizzes/{quiz_id}/answers",
        headers=bearer(token),
        json={
            "choice_id": wrong,
            "correct": True,
            "page": 99,
            "last_score": {"correct": 3, "total": 3},
            "correct_choice_id": wrong,
        },
    )
    assert graded.status_code == 200
    question = graded.json()["questions"][0]
    assert question["correct"] is False
    assert question["chosen_choice_id"] == wrong
    assert question["page"] in {2, 4}
    assert listed(bundle, token).json()["quizzes"][0]["last_score"] is None
