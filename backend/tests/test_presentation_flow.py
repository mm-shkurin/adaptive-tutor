import asyncio
from uuid import UUID

from tests.presentation_flow import MISSING, add_image, create, index, material, pieces, token
from tests.quiz_flow import ada
from tests.support import bearer, build


def test_creating_a_draft_stores_an_empty_presentation():
    bundle = build()
    access = token(bundle)
    created = create(bundle, access, "LinAlg")
    assert created.status_code == 201
    body = created.json()
    assert body["title"] == "LinAlg"
    assert body["status"] == "draft"
    assert body["slide_count"] == 0
    assert body["slides"] == []
    read_back = bundle.client.get(
        f"/api/v1/presentations/{body['id']}", headers=bearer(access)
    ).json()
    assert read_back == body
    materials = material(bundle, access)["documents"][0]
    assert materials["kind"] == "presentation"
    assert materials["name"] == "LinAlg"
    assert materials["status"] == "draft"
    assert materials["id"] == body["id"]


def test_omitted_title_becomes_the_default_draft_title():
    bundle = build()
    access = token(bundle)
    created = create(bundle, access, None)
    assert created.status_code == 201
    body = created.json()
    assert body["title"] == "Новая презентация"
    assert body["status"] == "draft"


def test_oversized_image_is_refused():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    huge = b"\xff\xd8\xff" + b"\x00" * (52_428_801 - 3)
    response = bundle.client.post(
        f"/api/v1/presentations/{presentation_id}/slides",
        headers={**bearer(access), "Idempotency-Key": "big"},
        files=[("images", ("huge.jpg", huge, "image/jpeg"))],
    )
    assert response.status_code == 400
    assert response.json() == {"code": "file_too_large", "message": "File is too large"}
    assert bundle.client.get(f"/api/v1/presentations/{presentation_id}", headers=bearer(access)).json()["slide_count"] == 0


def test_virus_on_image_refuses_the_add():
    bundle = build()
    access = token(bundle)
    bundle.virus.set_outcome("finds_virus")
    presentation_id = create(bundle, access).json()["id"]
    response = add_image(bundle, access, presentation_id)
    assert response.status_code == 400
    assert response.json() == {"code": "virus_detected", "message": "Virus detected"}
    assert bundle.client.get(f"/api/v1/presentations/{presentation_id}", headers=bearer(access)).json()["slide_count"] == 0


def test_same_idempotency_key_does_not_duplicate_slides():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    first = add_image(bundle, access, presentation_id, key="same-key")
    second = add_image(bundle, access, presentation_id, key="same-key")
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
    assert first.json()["slide_count"] == 1


def test_adding_slides_without_idempotency_key_is_refused():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    response = bundle.client.post(
        f"/api/v1/presentations/{presentation_id}/slides",
        headers=bearer(access),
        files=[("images", ("slide.jpg", b"\xff\xd8\xff\xd9", "image/jpeg"))],
    )
    assert response.status_code == 422
    assert (
        bundle.client.get(f"/api/v1/presentations/{presentation_id}", headers=bearer(access)).json()[
            "slide_count"
        ]
        == 0
    )


def test_index_with_zero_slides_is_refused():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    response = index(bundle, access, presentation_id)
    assert response.status_code == 400
    assert response.json() == {"code": "no_slides", "message": "Presentation has no slides"}
    assert bundle.client.get(f"/api/v1/presentations/{presentation_id}", headers=bearer(access)).json()["status"] == "draft"


def test_more_than_forty_slides_cannot_be_added():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    for slide_index in range(40):
        added = add_image(bundle, access, presentation_id, key=f"k-{slide_index}")
        assert added.status_code == 200
    refused = add_image(bundle, access, presentation_id, key="k-40")
    assert refused.status_code == 400
    assert refused.json() == {"code": "slide_limit", "message": "More than 40 slides"}
    assert (
        bundle.client.get(f"/api/v1/presentations/{presentation_id}", headers=bearer(access)).json()["slide_count"]
        == 40
    )


def test_successful_index_reaches_ready_with_searchable_pieces():
    bundle = build()
    access, owner_id = ada(bundle)
    presentation_id = create(bundle, access).json()["id"]
    added = add_image(bundle, access, presentation_id)
    slide_id = added.json()["slides"][0]["id"]
    bundle.ocr.set_text(UUID(slide_id), "hello slide")
    indexed = index(bundle, access, presentation_id, key="index-1")
    assert indexed.status_code == 202
    body = indexed.json()
    assert body["status"] == "ready"
    assert body["piece_count"] >= 1
    assert body["slides"][0]["empty"] is False
    assert asyncio.run(bundle.presentations.has_bytes(owner_id, UUID(presentation_id), UUID(slide_id))) is False
    materials = material(bundle, access)["documents"][0]
    assert materials["kind"] == "presentation"
    assert materials["status"] == "ready"
    replay = index(bundle, access, presentation_id, key="index-1")
    assert replay.status_code == 200
    assert len(pieces(bundle, presentation_id)) == 1


def test_empty_ocr_leaves_slide_empty_and_out_of_search():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    first = add_image(bundle, access, presentation_id, key="a1")
    second = add_image(bundle, access, presentation_id, key="a2")
    first_id = first.json()["slides"][0]["id"]
    second_id = second.json()["slides"][1]["id"]
    bundle.ocr.set_text(UUID(first_id), "visible text")
    bundle.ocr.set_text(UUID(second_id), "")
    indexed = index(bundle, access, presentation_id)
    body = indexed.json()
    assert body["status"] == "ready"
    assert body["slides"][0]["empty"] is False
    assert body["slides"][1]["empty"] is True
    found = pieces(bundle, presentation_id)
    assert len(found) == 1
    assert found[0] == "visible text"


def test_ready_text_edit_keeps_status_ready():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    slide_id = add_image(bundle, access, presentation_id).json()["slides"][0]["id"]
    bundle.ocr.set_text(UUID(slide_id), "before")
    index(bundle, access, presentation_id)
    patched = bundle.client.patch(
        f"/api/v1/presentations/{presentation_id}",
        headers=bearer(access),
        json={"slides": [{"id": slide_id, "text": "after"}]},
    )
    assert patched.status_code == 200
    body = patched.json()
    assert body["status"] == "ready"
    assert body["slides"][0]["text"] == "after"
    read_back = bundle.client.get(f"/api/v1/presentations/{presentation_id}", headers=bearer(access)).json()
    assert read_back["slides"][0]["text"] == "after"


def test_weak_ocr_may_call_formula_assist_once_per_slide():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    # Oversized jpeg body so thin OCR counts as weak.
    huge = b"\xff\xd8\xff" + b"\x00" * 12_000
    added = bundle.client.post(
        f"/api/v1/presentations/{presentation_id}/slides",
        headers={**bearer(access), "Idempotency-Key": "weak-1"},
        files=[("images", ("slide.jpg", huge, "image/jpeg"))],
    )
    slide_id = UUID(added.json()["slides"][0]["id"])
    bundle.ocr.set_text(slide_id, "x=?")
    bundle.formulas.set_result(slide_id, "x equals question", "x=?")
    indexed = index(bundle, access, presentation_id)
    assert indexed.status_code == 202
    body = indexed.json()
    assert body["slides"][0]["formula_phrase"] == "x equals question"
    assert body["slides"][0]["formula_latex"] == "x=?"
    assert bundle.formulas.calls == [slide_id]
    assert pieces(bundle, presentation_id) == ("x equals question",)


def test_formula_assist_timeout_keeps_ocr_text_without_formulas():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    huge = b"\xff\xd8\xff" + b"\x00" * 12_000
    added = bundle.client.post(
        f"/api/v1/presentations/{presentation_id}/slides",
        headers={**bearer(access), "Idempotency-Key": "weak-to"},
        files=[("images", ("slide.jpg", huge, "image/jpeg"))],
    )
    slide_id = UUID(added.json()["slides"][0]["id"])
    bundle.ocr.set_text(slide_id, "x=?")
    bundle.formulas.set_failure(slide_id)
    indexed = index(bundle, access, presentation_id)
    body = indexed.json()
    assert body["status"] == "ready"
    assert body["slides"][0]["text"] == "x=?"
    assert body["slides"][0]["formula_phrase"] is None
    assert body["slides"][0]["formula_latex"] is None
    assert pieces(bundle, presentation_id) == ("x=?",)


def test_reorder_changes_slide_positions():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    first = add_image(bundle, access, presentation_id, key="a").json()["slides"][0]["id"]
    second = add_image(bundle, access, presentation_id, key="b").json()["slides"][1]["id"]
    for slide_id in (first, second):
        bundle.ocr.set_text(UUID(slide_id), "text")
    index(bundle, access, presentation_id)
    patched = bundle.client.patch(
        f"/api/v1/presentations/{presentation_id}",
        headers=bearer(access),
        json={"slide_order": [second, first]},
    )
    assert patched.status_code == 200
    body = patched.json()
    assert [slide["id"] for slide in body["slides"]] == [second, first]
    assert body["slides"][0]["position"] == 1
    assert body["slides"][1]["position"] == 2


def test_deleting_the_only_slide_of_a_draft_leaves_slide_count_zero():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    slide_id = add_image(bundle, access, presentation_id).json()["slides"][0]["id"]
    deleted = bundle.client.delete(
        f"/api/v1/presentations/{presentation_id}/slides/{slide_id}",
        headers=bearer(access),
    )
    assert deleted.status_code == 200
    body = deleted.json()
    assert body["slide_count"] == 0
    assert body["status"] == "draft"
    assert body["slides"] == []


def test_delete_removes_searchability_and_refuses_later_get():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    slide_id = add_image(bundle, access, presentation_id).json()["slides"][0]["id"]
    bundle.ocr.set_text(UUID(slide_id), "token")
    index(bundle, access, presentation_id)
    assert len(pieces(bundle, presentation_id)) == 1
    deleted = bundle.client.delete(f"/api/v1/presentations/{presentation_id}", headers=bearer(access))
    assert deleted.status_code == 204
    missing = bundle.client.get(f"/api/v1/presentations/{presentation_id}", headers=bearer(access))
    assert missing.status_code == 404
    assert missing.json() == MISSING
    assert pieces(bundle, presentation_id) == ()