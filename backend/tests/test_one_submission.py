from pathlib import Path
from uuid import uuid4

from tests.support import bearer, build, sign_in

FIXTURES = Path(__file__).resolve().parents[2] / "acceptance" / "fixtures"
LECTURE = (FIXTURES / "lecture.pdf").read_bytes()


def _upload(bundle, token: str, key: str, name: str = "lecture.pdf"):
    return bundle.client.post(
        "/api/v1/documents",
        headers={**bearer(token), "Idempotency-Key": key},
        files={"file": (name, LECTURE, "application/pdf")},
    )


def test_same_submission_returns_same_document_without_a_second_row():
    bundle = build()
    token = sign_in(bundle).json()["access_token"]
    key = str(uuid4())
    first = _upload(bundle, token, key)
    second = _upload(bundle, token, key)
    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]
    listed = bundle.client.get("/api/v1/documents", headers=bearer(token), params={"page": 1})
    assert len(listed.json()["documents"]) == 1


def test_replay_does_not_consume_another_rate_slot():
    bundle = build()
    token = sign_in(bundle).json()["access_token"]
    key = str(uuid4())
    assert _upload(bundle, token, key).status_code == 201
    assert _upload(bundle, token, key).status_code == 200
    for index in range(4):
        assert _upload(bundle, token, str(uuid4()), f"extra-{index}.pdf").status_code == 201
    sixth = _upload(bundle, token, str(uuid4()), "sixth.pdf")
    assert sixth.status_code == 429
    assert sixth.json()["code"] == "rate_limited"
    listed = bundle.client.get("/api/v1/documents", headers=bearer(token), params={"page": 1})
    assert len(listed.json()["documents"]) == 5


def test_new_submission_of_same_bytes_creates_another_document():
    bundle = build()
    token = sign_in(bundle).json()["access_token"]
    first = _upload(bundle, token, str(uuid4()))
    second = _upload(bundle, token, str(uuid4()))
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] != second.json()["id"]
    listed = bundle.client.get("/api/v1/documents", headers=bearer(token), params={"page": 1})
    assert len(listed.json()["documents"]) == 2
    earlier = bundle.client.get(
        f"/api/v1/documents/{first.json()['id']}", headers=bearer(token)
    )
    assert earlier.status_code == 200
    assert earlier.json() == first.json()
