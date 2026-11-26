import asyncio
import json
from uuid import UUID, uuid4

from tests.support import JPEG, bearer, build, sign_in

MISSING = {"code": "presentation_not_found", "message": "Presentation was not found"}
PROGRESS_MISSING = {"code": "progress_not_found", "message": "Progress was not found"}


def token(bundle):
    return sign_in(bundle).json()["access_token"]


def create(bundle, token, title="LinAlg"):
    body = {} if title is None else {"title": title}
    return bundle.client.post(
        "/api/v1/presentations",
        headers=bearer(token),
        json=body,
    )


def add_image(bundle, token, presentation_id, key=None):
    key = key or str(uuid4())
    return bundle.client.post(
        f"/api/v1/presentations/{presentation_id}/slides",
        headers={**bearer(token), "Idempotency-Key": key},
        files=[("images", ("slide.jpg", JPEG, "image/jpeg"))],
    )


PDF_NOT_READY = {"code": "pdf_not_ready", "message": "PDF is not ready"}


def add_pdf_pages(bundle, token, presentation_id, pdf_document_id, pages, key=None):
    key = key or str(uuid4())
    return bundle.client.post(
        f"/api/v1/presentations/{presentation_id}/slides",
        headers={**bearer(token), "Idempotency-Key": key},
        data={
            "pdf_document_id": str(pdf_document_id),
            "pdf_pages": json.dumps(pages),
        },
    )


def index(bundle, token, presentation_id, key=None):
    key = key or str(uuid4())
    return bundle.client.post(
        f"/api/v1/presentations/{presentation_id}/index",
        headers={**bearer(token), "Idempotency-Key": key},
    )


def material(bundle, token):
    return bundle.client.get("/api/v1/documents", headers=bearer(token)).json()


def pieces(bundle, presentation_id):
    return asyncio.run(bundle.pieces.pieces(UUID(presentation_id)))