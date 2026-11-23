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
    finish(bundle, token, finished.json()["id"], "right")
    opened = post_quiz(bundle, token, document.id, 3)
    assert opened.status_code == 201
    grace_token, grace = neighbour(bundle)
    foreign = ready_pdf(bundle, grace, "grace.pdf")
    kept = post_quiz(bundle, grace_token, foreign.id, 3)
    assert kept.status_code == 201
    asyncio.run(QuizWipe(bundle.quizzes).wipe(None))
    assert len(bundle.quizzes.held(owner)) == 2
    assert len(bundle.quizzes.held(grace)) == 1
    deleted = bundle.client.delete("/api/v1/user", headers=bearer(token))
    assert deleted.status_code == 204
    assert bundle.quizzes.held(owner) == ()
    assert len(bundle.quizzes.held(grace)) == 1
    assert read(bundle, grace_token, kept.json()["id"]).status_code == 200
