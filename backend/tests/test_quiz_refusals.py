from uuid import uuid4

import pytest

from tests.quiz_flow import ada, post_quiz, ready_pdf, valid_body
from tests.support import bearer, build

EMPTY_TOPIC = {"code": "empty_topic", "message": "Topic is empty"}
BAD_COUNT = {"code": "invalid_question_count", "message": "Question count is not allowed"}
EMPTY_SEARCH = {"code": "empty_retrieval", "message": "Nothing was found for the topic"}
BAD_SHAPE = {"code": "generation_failed", "message": "Quiz could not be assembled"}


def _post(bundle, token, document_id, body, key=None):
    return bundle.client.post(
        "/api/v1/quizzes",
        headers={**bearer(token), "Idempotency-Key": key or str(uuid4())},
        json={"document_id": str(document_id), **body},
    )


def _refused(response, body, bundle, owner):
    assert response.status_code == 400
    assert response.json() == body
    assert bundle.quizzes.held(owner) == ()
    assert bundle.quiz_tutor.calls == []


@pytest.mark.parametrize("topic", ["", "   ", None])
def test_blank_topic_is_refused_and_nothing_is_stored(topic):
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "older.pdf")
    response = _post(bundle, token, document.id, {"topic": topic, "question_count": 5})
    _refused(response, EMPTY_TOPIC, bundle, owner)


def test_omitted_topic_is_refused_and_nothing_is_stored():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "older.pdf")
    response = _post(bundle, token, document.id, {"question_count": 5})
    _refused(response, EMPTY_TOPIC, bundle, owner)


@pytest.mark.parametrize("count", [None, 0, 1, 2, 4, 6, 9, -1, "five"])
def test_question_count_outside_3_5_and_8_is_refused(count):
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "older.pdf")
    response = _post(bundle, token, document.id, {"topic": "cells", "question_count": count})
    _refused(response, BAD_COUNT, bundle, owner)


def test_empty_search_stores_nothing_and_does_not_call_the_model():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "older.pdf", seed=False)
    response = post_quiz(bundle, token, document.id, 5)
    _refused(response, EMPTY_SEARCH, bundle, owner)


def _fewer():
    return valid_body(4)


def _more():
    return valid_body(6)


def _short_choices():
    payload = valid_body(5)
    payload["questions"][0]["choices"] = payload["questions"][0]["choices"][:3]
    return payload


def _no_correct():
    payload = valid_body(5)
    payload["questions"][0]["correct_index"] = None
    return payload


def _two_correct():
    payload = valid_body(5)
    payload["questions"][0]["correct_index"] = [0, 1]
    return payload


def _foreign_page():
    return valid_body(5, page=9)


@pytest.mark.parametrize(
    "shape",
    [_fewer, _more, _short_choices, _no_correct, _two_correct, _foreign_page],
)
def test_wrong_shape_stores_nothing_and_does_not_pin_the_attempt(shape):
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "older.pdf")
    key = str(uuid4())
    bundle.quiz_tutor.script(shape())
    refused = _post(bundle, token, document.id, {"topic": "cells", "question_count": 5}, key)
    assert refused.status_code == 400
    assert refused.json() == BAD_SHAPE
    assert bundle.quizzes.held(owner) == ()
    assert len(bundle.quiz_tutor.calls) == 1
    bundle.quiz_tutor.script(valid_body(5))
    created = _post(bundle, token, document.id, {"topic": "cells", "question_count": 5}, key)
    assert created.status_code == 201
    assert len(bundle.quizzes.held(owner)) == 1
    assert len(bundle.quiz_tutor.calls) == 2
