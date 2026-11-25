from uuid import UUID

from tests.presentation_flow import add_image, create, index, token
from tests.quiz_flow import ada, answer, post_quiz, ready_pdf, valid_body
from tests.support import build

NOT_READY = {"code": "document_not_ready", "message": "Document is not ready"}
NO_READY = {"code": "no_ready_document", "message": "No ready document"}


def test_draft_presentation_cannot_create_quiz():
    bundle = build()
    access, owner = ada(bundle)
    ready_pdf(bundle, owner, "anchor.pdf")
    presentation_id = create(bundle, access).json()["id"]
    response = post_quiz(bundle, access, presentation_id, 3, topic="slides")
    assert response.status_code == 400
    assert response.json() == NOT_READY


def test_draft_only_presentation_gets_no_ready_document():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    response = post_quiz(bundle, access, presentation_id, 3, topic="slides")
    assert response.status_code == 400
    assert response.json() == NO_READY


def test_ready_presentation_quiz_question_has_slide():
    bundle = build()
    access, owner = ada(bundle)
    presentation_id = create(bundle, access).json()["id"]
    slide_id = add_image(bundle, access, presentation_id).json()["slides"][0]["id"]
    bundle.ocr.set_text(UUID(slide_id), "eigenvalue slide")
    indexed = index(bundle, access, presentation_id)
    assert indexed.status_code == 202
    assert indexed.json()["status"] == "ready"
    created = post_quiz(bundle, access, presentation_id, 3, topic="eigen", page=1)
    assert created.status_code == 201
    stored = bundle.quizzes.held(owner)[0].questions[0]
    assert stored.slide == 1
    assert stored.page is None
    choice_id = created.json()["questions"][0]["choices"][0]["id"]
    graded = answer(bundle, access, created.json()["id"], choice_id).json()["questions"][0]
    assert graded["slide"] == 1
    assert graded.get("page") is None


def test_ready_pdf_quiz_stays_page_only():
    bundle = build()
    access, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "cells.pdf")
    created = post_quiz(bundle, access, document.id, 3, topic="cells", page=2)
    assert created.status_code == 201
    stored = bundle.quizzes.held(owner)[0].questions[0]
    assert stored.page == 2
    assert stored.slide is None
    choice_id = created.json()["questions"][0]["choices"][0]["id"]
    graded = answer(bundle, access, created.json()["id"], choice_id).json()["questions"][0]
    assert graded["page"] == 2
    assert graded.get("slide") is None