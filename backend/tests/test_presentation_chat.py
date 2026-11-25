import asyncio
from uuid import UUID

from tests.presentation_flow import add_image, create, index, token
from tests.quiz_flow import ada, ready_pdf
from tests.support import bearer, build

NOT_READY = {"code": "document_not_ready", "message": "Document is not ready"}


def open_chat(bundle, access, document_id):
    return bundle.client.post("/api/v1/chats/open", headers=bearer(access), json={"document_id": document_id})


def send_question(bundle, access, chat_id, text="Что на слайде?"):
    bundle.tutor.script("По материалу.")
    return bundle.client.post(
        f"/api/v1/chats/{chat_id}/messages",
        headers={**bearer(access), "Idempotency-Key": "chat-ask-1"},
        json={"text": text, "mode": "professor", "model": "auto"},
    )


def test_draft_presentation_cannot_bind_chat():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    response = open_chat(bundle, access, presentation_id)
    assert response.status_code == 400
    assert response.json() == NOT_READY


def test_ready_presentation_reply_cites_slide():
    bundle = build()
    access, owner = ada(bundle)
    presentation_id = create(bundle, access).json()["id"]
    slide_id = add_image(bundle, access, presentation_id).json()["slides"][0]["id"]
    bundle.ocr.set_text(UUID(slide_id), "eigenvalue slide")
    index(bundle, access, presentation_id)
    placed = asyncio.run(bundle.pieces.placed(UUID(presentation_id)))
    assert placed[0].slide == 1
    assert placed[0].page is None

    opened = open_chat(bundle, access, presentation_id)
    chat_id = opened.json()["id"]
    bundle.client.get(f"/api/v1/chats/{chat_id}", headers=bearer(access))

    attempt = send_question(bundle, access, chat_id)
    assert attempt.status_code == 200
    tutor = [line for line in attempt.json()["lines"] if line["role"] == "tutor"][-1]
    assert tutor["sources"][0]["slide"] == 1
    assert tutor["sources"][0].get("page") is None


def test_ready_pdf_chat_stays_page_only():
    bundle = build()
    access, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "cells.pdf")
    opened = open_chat(bundle, access, str(document.id))
    chat_id = opened.json()["id"]
    bundle.client.get(f"/api/v1/chats/{chat_id}", headers=bearer(access))

    attempt = send_question(bundle, access, chat_id)
    assert attempt.status_code == 200
    tutor = [line for line in attempt.json()["lines"] if line["role"] == "tutor"][-1]
    assert tutor["sources"][0]["page"] == 2
    assert tutor["sources"][0].get("slide") is None