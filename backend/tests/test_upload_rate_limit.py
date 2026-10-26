from pathlib import Path
from uuid import uuid4

from tests.support import bearer, build, sign_in

FIXTURES = Path(__file__).resolve().parents[2] / "acceptance" / "fixtures"
LECTURE = (FIXTURES / "lecture.pdf").read_bytes()


def _upload(bundle, token: str, name: str = "lecture.pdf"):
    return bundle.client.post(
        "/api/v1/documents",
        headers={**bearer(token), "Idempotency-Key": str(uuid4())},
        files={"file": (name, LECTURE, "application/pdf")},
    )


def test_sixth_upload_returns_rate_limited_and_keeps_five():
    bundle = build()
    token = sign_in(bundle).json()["access_token"]
    for index in range(5):
        assert _upload(bundle, token, f"lecture-{index}.pdf").status_code == 201
    refused = _upload(bundle, token, "sixth.pdf")
    assert refused.status_code == 429
    assert refused.json() == {
        "code": "rate_limited",
        "message": "Too many uploads in this minute",
    }
    listed = bundle.client.get("/api/v1/documents", headers=bearer(token), params={"page": 1})
    assert listed.status_code == 200
    assert len(listed.json()["documents"]) == 5


def test_upload_after_minute_opens_is_accepted():
    bundle = build()
    token = sign_in(bundle).json()["access_token"]
    for index in range(5):
        assert _upload(bundle, token, f"lecture-{index}.pdf").status_code == 201
    bundle.clock.advance(60 - bundle.clock.moment.second - 1)
    assert _upload(bundle, token, "still-this-minute.pdf").status_code == 429
    bundle.clock.advance(2)
    accepted = _upload(bundle, token, "next-minute.pdf")
    assert accepted.status_code == 201
    listed = bundle.client.get("/api/v1/documents", headers=bearer(token), params={"page": 1})
    assert len(listed.json()["documents"]) == 6


def test_unreadable_upload_count_returns_rate_unavailable():
    bundle = build()
    token = sign_in(bundle).json()["access_token"]
    bundle.rates.fail_reads = True
    refused = _upload(bundle, token)
    assert refused.status_code == 429
    assert refused.json() == {
        "code": "rate_unavailable",
        "message": "Upload limit could not be checked",
    }
    listed = bundle.client.get("/api/v1/documents", headers=bearer(token), params={"page": 1})
    assert listed.json() == {"documents": [], "has_next": False}
