from uuid import uuid4

import pytest

from tests.quiz_flow import ada, advance, answer, neighbour, post_quiz, read, ready_pdf, retry
from tests.support import bearer, build

MISSING = {"code": "quiz_not_found", "message": "Quiz was not found"}


def _world():
    bundle = build()
    token, _owner = ada(bundle)
    grace_token, grace = neighbour(bundle)
    document = ready_pdf(bundle, grace, "grace.pdf")
    created = post_quiz(bundle, grace_token, document.id, 3, topic="neighbour topic")
    assert created.status_code == 201
    quiz_id = created.json()["id"]
    quiz_before = read(bundle, grace_token, quiz_id).json()
    pdf_before = bundle.client.get(
        f"/api/v1/documents/{document.id}", headers=bearer(grace_token)
    ).json()
    calls = len(bundle.quiz_tutor.calls)
    return bundle, token, grace_token, document, quiz_id, quiz_before, pdf_before, calls


def _unchanged(bundle, grace_token, document, quiz_id, quiz_before, pdf_before, calls):
    assert read(bundle, grace_token, quiz_id).json() == quiz_before
    pdf_after = bundle.client.get(
        f"/api/v1/documents/{document.id}", headers=bearer(grace_token)
    ).json()
    assert pdf_after == pdf_before
    assert len(bundle.quiz_tutor.calls) == calls
    assert bundle.quizzes.count() == 1


@pytest.mark.parametrize("ask", ["read", "answer", "advance", "retry", "missing"])
def test_another_persons_quiz_is_refused_like_a_missing_quiz(ask):
    bundle, token, grace_token, document, quiz_id, quiz_before, pdf_before, calls = _world()
    target = quiz_id if ask != "missing" else str(uuid4())
    if ask == "answer":
        response = answer(bundle, token, target, str(uuid4()))
    elif ask == "advance":
        response = advance(bundle, token, target)
    elif ask == "retry":
        response = retry(bundle, token, target)
    else:
        response = read(bundle, token, target)
    assert response.status_code == 404
    assert response.json() == MISSING
    _unchanged(bundle, grace_token, document, quiz_id, quiz_before, pdf_before, calls)


@pytest.mark.parametrize("foreign", [True, False])
def test_create_on_a_foreign_or_missing_document_is_a_missing_quiz(foreign):
    bundle, token, grace_token, document, quiz_id, quiz_before, pdf_before, calls = _world()
    document_id = document.id if foreign else uuid4()
    response = post_quiz(bundle, token, document_id, 3, topic="cells")
    assert response.status_code == 404
    assert response.json() == MISSING
    _unchanged(bundle, grace_token, document, quiz_id, quiz_before, pdf_before, calls)
