from uuid import uuid4

import pytest

from tests.presentation_flow import PDF_NOT_READY, add_pdf_pages, create
from tests.quiz_flow import ada, neighbour, ready_pdf, unready_pdf
from tests.support import bearer, build

PDF_PAGE_MISSING = {"code": "pdf_page_missing", "message": "PDF page was not found"}


@pytest.mark.parametrize("state", ["waiting", "indexing", "failed", "missing"])
def test_pdf_page_slide_requires_a_ready_owned_pdf(state):
    bundle = build()
    access, owner = ada(bundle)
    presentation_id = create(bundle, access).json()["id"]
    if state == "missing":
        pdf_id = uuid4()
    else:
        pdf = unready_pdf(bundle, owner, f"{state}.pdf", state)
        pdf_id = pdf.id
    response = add_pdf_pages(bundle, access, presentation_id, pdf_id, [1])
    assert response.status_code == 400
    assert response.json() == PDF_NOT_READY
    read_back = bundle.client.get(f"/api/v1/presentations/{presentation_id}", headers=bearer(access)).json()
    assert read_back["slide_count"] == 0


def test_neighbour_ready_pdf_cannot_be_added():
    bundle = build()
    access, _ = ada(bundle)
    _, neighbour_owner = neighbour(bundle)
    foreign = ready_pdf(bundle, neighbour_owner, "secret.pdf")
    presentation_id = create(bundle, access).json()["id"]
    response = add_pdf_pages(bundle, access, presentation_id, foreign.id, [1])
    assert response.status_code == 400
    assert response.json() == PDF_NOT_READY
    read_back = bundle.client.get(f"/api/v1/presentations/{presentation_id}", headers=bearer(access)).json()
    assert read_back["slide_count"] == 0


def test_ready_pdf_pages_are_stored_as_pdf_page_slides():
    bundle = build()
    access, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "lecture.pdf")
    presentation_id = create(bundle, access).json()["id"]
    response = add_pdf_pages(bundle, access, presentation_id, document.id, [1, 3])
    assert response.status_code == 200
    body = response.json()
    assert body["slide_count"] == 2
    first, second = body["slides"]
    assert first["source"] == "pdf_page"
    assert first["pdf_document_id"] == str(document.id)
    assert first["pdf_page"] == 1
    assert first["position"] == 1
    assert second["source"] == "pdf_page"
    assert second["pdf_page"] == 3
    assert second["position"] == 2


def test_pdf_page_beyond_count_is_refused():
    bundle = build()
    access, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "short.pdf")
    presentation_id = create(bundle, access).json()["id"]
    response = add_pdf_pages(bundle, access, presentation_id, document.id, [4])
    assert response.status_code == 400
    assert response.json() == PDF_PAGE_MISSING
    read_back = bundle.client.get(f"/api/v1/presentations/{presentation_id}", headers=bearer(access)).json()
    assert read_back["slide_count"] == 0