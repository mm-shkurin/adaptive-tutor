from uuid import UUID

from domain.document.document import DELETED_SOURCE_NAME
from tests.presentation_flow import add_image, create, index, token
from tests.quiz_flow import ada, post_quiz
from tests.support import bearer, build


def test_quiz_list_shows_tombstone_after_presentation_delete():
    bundle = build()
    access, _owner = ada(bundle)
    presentation_id = create(bundle, access, "LinAlg").json()["id"]
    slide_id = add_image(bundle, access, presentation_id).json()["slides"][0]["id"]
    bundle.ocr.set_text(UUID(slide_id), "matrix text")
    index(bundle, access, presentation_id)
    created = post_quiz(bundle, access, presentation_id, 3, topic="matrix", page=1)
    assert created.status_code == 201, created.json()
    quiz_id = created.json()["id"]
    deleted = bundle.client.delete(f"/api/v1/presentations/{presentation_id}", headers=bearer(access))
    assert deleted.status_code == 204
    cards = bundle.client.get("/api/v1/quizzes", headers=bearer(access)).json()["quizzes"]
    card = next(item for item in cards if item["id"] == quiz_id)
    assert card["document_name"] == DELETED_SOURCE_NAME
    opened = bundle.client.get(f"/api/v1/quizzes/{quiz_id}", headers=bearer(access)).json()
    assert opened["document_name"] == DELETED_SOURCE_NAME


def test_chat_list_shows_tombstone_after_presentation_delete():
    bundle = build()
    access, _owner = ada(bundle)
    presentation_id = create(bundle, access, "LinAlg").json()["id"]
    slide_id = add_image(bundle, access, presentation_id).json()["slides"][0]["id"]
    bundle.ocr.set_text(UUID(slide_id), "matrix text")
    index(bundle, access, presentation_id)
    opened = bundle.client.post(
        "/api/v1/chats/open",
        headers=bearer(access),
        json={"document_id": presentation_id},
    )
    assert opened.status_code in {200, 201}, opened.json()
    chat_id = opened.json()["id"]
    deleted = bundle.client.delete(f"/api/v1/presentations/{presentation_id}", headers=bearer(access))
    assert deleted.status_code == 204
    chats = bundle.client.get("/api/v1/chats", headers=bearer(access)).json()["chats"]
    card = next(item for item in chats if item["id"] == chat_id)
    assert card["document_name"] == DELETED_SOURCE_NAME
    detail = bundle.client.get(f"/api/v1/chats/{chat_id}", headers=bearer(access)).json()
    assert detail["document_name"] == DELETED_SOURCE_NAME
