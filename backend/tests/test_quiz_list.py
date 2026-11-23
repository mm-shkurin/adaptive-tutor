from uuid import UUID

from tests.quiz_flow import ada, advance, answer, listed, neighbour, post_quiz, read, ready_pdf, retry
from tests.support import build


def _score(bundle, token, quiz_id, picks):
    detail = read(bundle, token, quiz_id).json()
    for pick in picks:
        chosen = detail["questions"][detail["current_index"]]["choices"][pick]["id"]
        assert answer(bundle, token, quiz_id, chosen).status_code == 200
        advanced = advance(bundle, token, quiz_id)
        assert advanced.status_code == 200
        detail = advanced.json()
    return detail


def test_empty_quiz_list_is_the_persons_own_list():
    bundle = build()
    token, _owner = ada(bundle)
    grace_token, grace = neighbour(bundle)
    foreign = ready_pdf(bundle, grace, "grace.pdf")
    other = post_quiz(bundle, grace_token, foreign.id, 3, topic="neighbour topic")
    assert other.status_code == 201
    response = listed(bundle, token)
    assert response.status_code == 200
    assert response.json() == {"quizzes": []}
    assert "neighbour topic" not in response.text


def test_list_is_newest_first_and_an_open_attempt_keeps_the_completed_score():
    bundle = build()
    token, owner = ada(bundle)
    older_doc = ready_pdf(bundle, owner, "older.pdf")
    older = post_quiz(bundle, token, older_doc.id, 3, topic="mitosis")
    assert older.status_code == 201
    assert _score(bundle, token, older.json()["id"], [0, 1, 1])["last_score"] == {
        "correct": 1,
        "total": 3,
    }
    bundle.clock.advance(60)
    replay_doc = ready_pdf(bundle, owner, "lecture.pdf")
    replay = post_quiz(bundle, token, replay_doc.id, 5, topic="cells")
    assert replay.status_code == 201
    assert _score(bundle, token, replay.json()["id"], [0, 0, 1, 1, 1])["last_score"] == {
        "correct": 2,
        "total": 5,
    }
    assert retry(bundle, token, replay.json()["id"]).status_code == 200
    fresh_doc = ready_pdf(bundle, owner, "fresh.pdf")
    fresh = post_quiz(bundle, token, fresh_doc.id, 5, topic="osmosis")
    assert fresh.status_code == 201
    bundle.clock.advance(60)
    grace_token, grace = neighbour(bundle)
    foreign = ready_pdf(bundle, grace, "grace.pdf")
    other = post_quiz(bundle, grace_token, foreign.id, 3, topic="neighbour topic")
    assert other.status_code == 201
    response = listed(bundle, token)
    assert response.status_code == 200
    cards = response.json()["quizzes"]
    assert [card["id"] for card in cards[2:]] == [older.json()["id"]]
    pair = [UUID(card["id"]) for card in cards[:2]]
    assert pair == sorted([UUID(replay.json()["id"]), UUID(fresh.json()["id"])], reverse=True)
    by_id = {card["id"]: card for card in cards}
    assert by_id[replay.json()["id"]]["last_score"] == {"correct": 2, "total": 5}
    assert by_id[older.json()["id"]]["last_score"] == {"correct": 1, "total": 3}
    assert by_id[fresh.json()["id"]]["last_score"] is None
    assert by_id[older.json()["id"]]["document_name"] == "older.pdf"
    assert by_id[older.json()["id"]]["topic"] == "mitosis"
    assert by_id[older.json()["id"]]["question_count"] == 3
    assert by_id[replay.json()["id"]]["document_name"] == "lecture.pdf"
    assert by_id[replay.json()["id"]]["topic"] == "cells"
    assert by_id[replay.json()["id"]]["question_count"] == 5
    assert by_id[fresh.json()["id"]]["document_name"] == "fresh.pdf"
    assert by_id[fresh.json()["id"]]["topic"] == "osmosis"
    assert by_id[fresh.json()["id"]]["question_count"] == 5
    for card in cards:
        assert "correct_choice_id" not in card
        assert "correct" not in card
    assert other.json()["id"] not in by_id
    assert "neighbour topic" not in response.text
    opened = read(bundle, token, replay.json()["id"]).json()
    assert opened["status"] == "take"
    assert opened["current_index"] == 0
    assert opened["last_score"] == {"correct": 2, "total": 5}
