import asyncio
from uuid import uuid4

import pymupdf
import pytest

from domain.document.document import Document
from tests.presentation_flow import PDF_NOT_READY, add_pdf_pages, create, index, pieces
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


def test_pdf_page_slide_index_yields_searchable_text():
    bundle = build()
    access, owner = ada(bundle)
    content = _pdf_with_text({1: "mitochondria", 3: "chloroplast"})
    document = Document.accepted("bio.pdf", len(content)).ready(3, 2)
    asyncio.run(bundle.intake.store(owner, document, content, str(uuid4())))
    presentation_id = create(bundle, access).json()["id"]
    add_pdf_pages(bundle, access, presentation_id, document.id, [1, 3])
    indexed = index(bundle, access, presentation_id, key="pdf-index-1")
    assert indexed.status_code == 202
    body = indexed.json()
    assert body["status"] == "ready"
    assert body["piece_count"] == 2
    assert body["slides"][0]["empty"] is False
    assert "mitochondria" in body["slides"][0]["text"]
    stored = pieces(bundle, presentation_id)
    assert "mitochondria" in stored[0]
    assert any("chloroplast" in piece for piece in stored)


def _pdf_with_text(page_texts: dict[int, str]) -> bytes:
    document = pymupdf.open()
    try:
        last = max(page_texts)
        for number in range(1, last + 1):
            page = document.new_page()
            if number in page_texts:
                page.insert_text((72, 72), page_texts[number])
        return document.tobytes()
    finally:
        document.close()


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