import asyncio
from uuid import UUID

from tests.presentation_flow import MISSING, add_image, create, index, material, pieces, token
from tests.quiz_flow import ada
from tests.support import bearer, build


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
