import pytest

from tests.quiz_flow import ada, advance, answer, hidden, listed, post_quiz, read, ready_pdf
from tests.support import build


def _open(count=5):
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "older.pdf")
    created = post_quiz(bundle, token, document.id, count)
    assert created.status_code == 201
    return bundle, token, created.json()


@pytest.mark.parametrize("pick,right", [(0, True), (1, False)])
def test_a_choice_is_graded_once_from_the_stored_correct_choice(pick, right):
    bundle, token, quiz = _open()
    calls = len(bundle.quiz_tutor.calls)
    question = quiz["questions"][0]
    chosen = question["choices"][pick]["id"]
    other = question["choices"][1 - pick]["id"]
    first = answer(bundle, token, quiz["id"], chosen)
    assert first.status_code == 200
    graded = first.json()["questions"][0]
    assert graded["correct"] is right
    assert graded["chosen_choice_id"] == chosen
    assert graded["correct_choice_id"] == question["choices"][0]["id"]
    assert isinstance(graded["page"], int)
    assert graded["page"] in {2, 4}
    assert "slide" not in first.text
    second = answer(bundle, token, quiz["id"], other)
    assert second.status_code == 200
    again = second.json()["questions"][0]
    assert again["correct"] is right
    assert again["chosen_choice_id"] == chosen
    assert again["correct_choice_id"] == graded["correct_choice_id"]
    assert len(bundle.quiz_tutor.calls) == calls


def test_advance_before_a_choice_is_refused():
    bundle, token, quiz = _open()
    calls = len(bundle.quiz_tutor.calls)
    refused = advance(bundle, token, quiz["id"])
    assert refused.status_code == 400
    assert refused.json() == {"code": "unanswered", "message": "The question is not answered"}
    stayed = read(bundle, token, quiz["id"]).json()
    assert stayed["current_index"] == 0
    hidden(stayed["questions"][0])
    chosen = quiz["questions"][0]["choices"][0]["id"]
    assert answer(bundle, token, quiz["id"], chosen).status_code == 200
    assert advance(bundle, token, quiz["id"]).status_code == 200
    again = advance(bundle, token, quiz["id"])
    assert again.status_code == 400
    assert again.json() == {"code": "unanswered", "message": "The question is not answered"}
    later = read(bundle, token, quiz["id"]).json()
    assert later["current_index"] == 1
    hidden(later["questions"][1])
    assert len(bundle.quiz_tutor.calls) == calls


def test_next_opens_the_following_question_and_keeps_the_grade():
    bundle, token, quiz = _open()
    calls = len(bundle.quiz_tutor.calls)
    chosen = quiz["questions"][0]["choices"][1]["id"]
    graded = answer(bundle, token, quiz["id"], chosen).json()["questions"][0]
    nxt = advance(bundle, token, quiz["id"])
    assert nxt.status_code == 200
    body = nxt.json()
    assert body["status"] == "take"
    assert body["current_index"] == 1
    assert body["questions"][0]["chosen_choice_id"] == graded["chosen_choice_id"]
    assert body["questions"][0]["correct"] == graded["correct"]
    hidden(body["questions"][1])
    assert listed(bundle, token).json()["quizzes"][0]["last_score"] is None
    opened = read(bundle, token, quiz["id"]).json()
    assert opened["current_index"] == 1
    assert len(bundle.quiz_tutor.calls) == calls
