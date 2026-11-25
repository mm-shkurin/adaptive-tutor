from uuid import UUID, uuid4

from domain.presentation.parsed_office import ParsedOfficeSlide
from tests.presentation_flow import create, index, pieces, token
from tests.support import JPEG, bearer, build

OFFICE = b"PK" + b"\x00" * 32


def add_office(bundle, token, presentation_id, key=None, payload=OFFICE):
    key = key or str(uuid4())
    return bundle.client.post(
        f"/api/v1/presentations/{presentation_id}/slides",
        headers={**bearer(token), "Idempotency-Key": key},
        files={"file": ("deck.pptx", payload, "application/vnd.openxmlformats-officedocument.presentationml.presentation")},
    )


def test_office_import_adds_parsed_slides():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    bundle.office.set_slides("pptx", (ParsedOfficeSlide("Slide A", None), ParsedOfficeSlide("Slide B", None)))
    response = add_office(bundle, access, presentation_id)
    assert response.status_code == 200
    body = response.json()
    assert body["slide_count"] == 2
    assert body["slides"][0]["source"] == "pptx"
    assert body["slides"][0]["text"] == "Slide A"
    assert body["slides"][1]["text"] == "Slide B"


def test_virus_on_office_refuses_the_add():
    bundle = build()
    access = token(bundle)
    bundle.virus.set_outcome("finds_virus")
    presentation_id = create(bundle, access).json()["id"]
    response = add_office(bundle, access, presentation_id)
    assert response.status_code == 400
    assert response.json() == {"code": "virus_detected", "message": "Virus detected"}
    assert bundle.client.get(f"/api/v1/presentations/{presentation_id}", headers=bearer(access)).json()["slide_count"] == 0


def test_invalid_office_is_refused():
    bundle = build()
    access = token(bundle)
    bundle.office.refuse()
    presentation_id = create(bundle, access).json()["id"]
    response = add_office(bundle, access, presentation_id)
    assert response.status_code == 400
    assert response.json() == {"code": "invalid_office", "message": "Office file is not supported"}


def test_office_over_forty_slides_is_refused():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    for slide_index in range(39):
        added = add_office(bundle, access, presentation_id, key=f"k-{slide_index}")
        assert added.status_code == 200
    bundle.office.set_slides("pptx", tuple(ParsedOfficeSlide(f"x{i}", None) for i in range(2)))
    refused = add_office(bundle, access, presentation_id, key="over")
    assert refused.status_code == 400
    assert refused.json() == {"code": "slide_limit", "message": "More than 40 slides"}
    assert bundle.client.get(f"/api/v1/presentations/{presentation_id}", headers=bearer(access)).json()["slide_count"] == 39


def test_office_text_indexes_without_ocr():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    bundle.office.set_slides("docx", (ParsedOfficeSlide("Week notes", None),))
    add_office(bundle, access, presentation_id)
    indexed = index(bundle, access, presentation_id)
    assert indexed.status_code == 202
    body = indexed.json()
    assert body["status"] == "ready"
    assert body["slides"][0]["source"] == "docx"
    assert body["slides"][0]["text"] == "Week notes"
    assert pieces(bundle, presentation_id) == ("Week notes",)


def test_office_embedded_image_uses_ocr_path():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    bundle.office.set_slides("pptx", (ParsedOfficeSlide("Title", JPEG),))
    added = add_office(bundle, access, presentation_id)
    slide_id = added.json()["slides"][0]["id"]
    bundle.ocr.set_text(UUID(slide_id), "ocr body")
    indexed = index(bundle, access, presentation_id, key="office-img")
    assert indexed.json()["slides"][0]["text"] == "Title\n\nocr body"