import asyncio

from tests.quiz_flow import ada, finish, neighbour, post_quiz, read, ready_pdf
from tests.support import bearer, build
from usecase.quiz.wipe import QuizWipe


def test_deleting_the_account_removes_that_persons_quizzes_only():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "ada.pdf")
    finished = post_quiz(bundle, token, document.id, 3)
    assert finished.status_code == 201
    done = finish(bundle, token, finished.json()["id"], "right")
    assert done["status"] == "result"
    opened = post_quiz(bundle, token, document.id, 3)
    assert opened.status_code == 201
    assert opened.json()["status"] == "take"
    grace_token, grace = neighbour(bundle)
    foreign = ready_pdf(bundle, grace, "grace.pdf")
    kept = post_quiz(bundle, grace_token, foreign.id, 3)
    assert kept.status_code == 201
    kept_id = kept.json()["id"]
    asyncio.run(QuizWipe(bundle.quizzes).wipe(None))
    assert len(bundle.quizzes.held(owner)) == 2
    assert len(bundle.quizzes.held(grace)) == 1
    deleted = bundle.client.delete("/api/v1/user", headers=bearer(token))
    assert deleted.status_code == 204
    assert bundle.quizzes.held(owner) == ()
    neighbour_quiz = bundle.quizzes.held(grace)[0]
    assert str(neighbour_quiz.id) == kept_id
    assert neighbour_quiz.open_attempt is not None
    assert neighbour_quiz.open_attempt.index == 0
    still_open = read(bundle, grace_token, kept_id).json()
    assert still_open["status"] == "take"
    assert still_open["current_index"] == 0
