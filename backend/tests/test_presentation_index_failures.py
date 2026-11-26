from uuid import UUID

from tests.presentation_flow import add_image, create, index, material, pieces, token
from tests.support import bearer, build

VIRUS = {"code": "virus_detected", "message": "Virus detected"}


def test_virus_timeout_refuses_the_slide_add():
    bundle = build()
    access = token(bundle)
    bundle.virus.set_outcome("times_out")
    presentation_id = create(bundle, access).json()["id"]
    response = add_image(bundle, access, presentation_id)
    assert response.status_code == 400
    assert response.json() == VIRUS
    assert bundle.client.get(
        f"/api/v1/presentations/{presentation_id}", headers=bearer(access)
    ).json()["slide_count"] == 0


def test_ocr_channel_failure_fails_index_without_pieces():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    add_image(bundle, access, presentation_id)
    bundle.ocr.fail()
    indexed = index(bundle, access, presentation_id)
    assert indexed.status_code == 202
    body = indexed.json()
    assert body["status"] == "failed"
    assert body["error"] == "ocr refused"
    assert pieces(bundle, presentation_id) == ()
    assert material(bundle, access)["documents"][0]["status"] == "failed"


def test_embeddings_failure_fails_the_index():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    slide_id = add_image(bundle, access, presentation_id).json()["slides"][0]["id"]
    bundle.ocr.set_text(UUID(slide_id), "searchable")
    bundle.pieces.dead = True
    indexed = index(bundle, access, presentation_id)
    assert indexed.status_code == 202
    body = indexed.json()
    assert body["status"] == "failed"
    assert body["error"] == "search store refused"
    bundle.pieces.dead = False
    assert pieces(bundle, presentation_id) == ()


def test_app_uses_fake_ocr_and_formula_ports():
    bundle = build()
    assert bundle.ocr.__class__.__name__ == "FakeOcr"
    assert bundle.formulas.__class__.__name__ == "FakeFormulaAssist"


def test_missing_virus_configuration_refuses_slide_bytes():
    bundle = build()
    access = token(bundle)
    bundle.virus.set_outcome("answers_unreadable")
    presentation_id = create(bundle, access).json()["id"]
    response = add_image(bundle, access, presentation_id)
    assert response.status_code == 400
    assert response.json() == VIRUS
    assert bundle.client.get(
        f"/api/v1/presentations/{presentation_id}", headers=bearer(access)
    ).json()["slide_count"] == 0
