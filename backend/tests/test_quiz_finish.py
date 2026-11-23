import pytest

from tests.quiz_flow import (
    ada,
    advance,
    answer,
    finish,
    hidden,
    listed,
    post_quiz,
    read,
    ready_pdf,
    retry,
)
from tests.support import build


def _open(count):
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "lecture.pdf")
    created = post_quiz(bundle, token, document.id, count)
    assert created.status_code == 201
    return bundle, token, created.json()


def _marks(detail):
    return [
        (question["id"], tuple(choice["text"] for choice in question["choices"]))
        for question in detail["questions"]
    ]


@pytest.mark.parametrize("count,how,correct", [(5, "wrong", 0), (3, "right", 3), (8, "right", 8)])
def test_finish_records_the_score_and_clears_the_open_attempt(count, how, correct):
    bundle, token, quiz = _open(count)
    calls = len(bundle.quiz_tutor.calls)
    done = finish(bundle, token, quiz["id"], how)
    assert done["status"] == "result"
    assert "current_index" not in done
    assert done["last_score"] == {"correct": correct, "total": count}
    assert len(done["questions"]) == count
    for question in done["questions"]:
        assert question["chosen_choice_id"]
        assert question["correct_choice_id"]
        assert question["correct"] is (how == "right")
        assert isinstance(question["page"], int)
    assert "slide" not in str(done)
    cards = listed(bundle, token).json()["quizzes"]
    assert cards[0]["last_score"] == {"correct": correct, "total": count}
    assert len(bundle.quiz_tutor.calls) == calls


def test_opening_the_quiz_again_continues_at_the_saved_question():
    bundle, token, quiz = _open(3)
    calls = len(bundle.quiz_tutor.calls)
    assert finish(bundle, token, quiz["id"], "wrong")["last_score"] == {"correct": 0, "total": 3}
    assert listed(bundle, token).json()["quizzes"][0]["last_score"] == {"correct": 0, "total": 3}
    again = retry(bundle, token, quiz["id"])
    assert again.status_code == 200
    hidden(again.json()["questions"][0])
    first = again.json()["questions"][0]["choices"][1]["id"]
    graded = answer(bundle, token, quiz["id"], first).json()["questions"][0]
    assert advance(bundle, token, quiz["id"]).status_code == 200
    resumed = read(bundle, token, quiz["id"]).json()
    assert resumed["status"] == "take"
    assert resumed["current_index"] == 1
    assert resumed["questions"][0]["correct"] is graded["correct"]
    assert resumed["questions"][0]["chosen_choice_id"] == graded["chosen_choice_id"]
    hidden(resumed["questions"][1])
    assert listed(bundle, token).json()["quizzes"][0]["last_score"] == {"correct": 0, "total": 3}
    assert len(bundle.quiz_tutor.calls) == calls


def test_play_again_keeps_the_previous_score_until_the_new_finish():
    bundle, token, quiz = _open(5)
    calls = len(bundle.quiz_tutor.calls)
    done = finish(bundle, token, quiz["id"], "wrong")
    assert done["last_score"] == {"correct": 0, "total": 5}
    marks = _marks(done)
    again = retry(bundle, token, quiz["id"])
    assert again.status_code == 200
    body = again.json()
    assert body["status"] == "take"
    assert body["current_index"] == 0
    assert _marks(body) == marks
    for question in body["questions"]:
        hidden(question)
    assert listed(bundle, token).json()["quizzes"][0]["last_score"] == {"correct": 0, "total": 5}
    redone = finish(bundle, token, quiz["id"], "right")
    assert redone["last_score"] == {"correct": 5, "total": 5}
    cards = listed(bundle, token).json()["quizzes"]
    assert len(cards) == 1
    assert cards[0]["last_score"] == {"correct": 5, "total": 5}
    assert len(bundle.quiz_tutor.calls) == calls
