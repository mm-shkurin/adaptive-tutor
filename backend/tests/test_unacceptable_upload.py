from pathlib import Path
from uuid import uuid4

from tests.support import bearer, build, sign_in

FIXTURES = Path(__file__).resolve().parents[2] / "acceptance" / "fixtures"
MIN_BYTES = 1_048_576
LECTURE = (FIXTURES / "lecture.pdf").read_bytes()
EMPTY = (FIXTURES / "empty_text.pdf").read_bytes()
ENCRYPTED = (FIXTURES / "encrypted.pdf").read_bytes()


def _token(bundle) -> str:
    return sign_in(bundle).json()["access_token"]


def _post(bundle, token: str, **kwargs):
    return bundle.client.post(
        "/api/v1/documents",
        headers={**bearer(token), "Idempotency-Key": str(uuid4())},
        **kwargs,
    )


def test_missing_file_is_refused_without_a_row():
    bundle = build()
    token = _token(bundle)
    assert _post(bundle, token, files={"file": ("ok.pdf", LECTURE, "application/pdf")}).status_code == 201
    refused = _post(bundle, token)
    assert refused.status_code == 400
    assert refused.json() == {"code": "file_missing", "message": "File is missing"}
    listed = bundle.client.get("/api/v1/documents", headers=bearer(token), params={"page": 1})
    assert len(listed.json()["documents"]) == 1


def test_empty_file_name_is_refused_without_a_row():
    bundle = build()
    token = _token(bundle)
    assert _post(bundle, token, files={"file": ("ok.pdf", LECTURE, "application/pdf")}).status_code == 201
    body = b"%PDF-1.4\n" + b"x" * (MIN_BYTES - 9)
    refused = _post(bundle, token, files={"file": ("", body, "application/pdf")})
    assert refused.status_code == 400
    assert refused.json() == {"code": "name_missing", "message": "File name is missing"}
    listed = bundle.client.get("/api/v1/documents", headers=bearer(token), params={"page": 1})
    assert len(listed.json()["documents"]) == 1


def test_empty_and_encrypted_pdfs_are_refused():
    bundle = build()
    token = _token(bundle)
    empty = _post(bundle, token, files={"file": ("blank.pdf", EMPTY, "application/pdf")})
    assert empty.status_code == 400
    assert empty.json() == {"code": "empty_pdf", "message": "PDF has no text"}
    locked = _post(bundle, token, files={"file": ("locked.pdf", ENCRYPTED, "application/pdf")})
    assert locked.status_code == 400
    assert locked.json() == {"code": "encrypted_pdf", "message": "PDF is encrypted"}
