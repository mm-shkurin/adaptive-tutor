from pathlib import Path
from uuid import uuid4

from domain.document.file_name import DocumentNameError, canonical_name
from tests.support import bearer, build, sign_in

FIXTURES = Path(__file__).resolve().parents[2] / "acceptance" / "fixtures"
LECTURE = (FIXTURES / "lecture.pdf").read_bytes()
SPLIT_LETTER_NAME = ("я" * 254) + "е\u0301"
NAIVE_BROKEN = SPLIT_LETTER_NAME[:255]


def test_canonical_name_keeps_a_letter_that_spans_the_code_point_limit():
    kept = canonical_name(SPLIT_LETTER_NAME)
    assert kept == SPLIT_LETTER_NAME
    assert kept != NAIVE_BROKEN
    assert "\ufffd" not in kept


def test_canonical_name_refuses_two_hundred_fifty_six_graphemes():
    try:
        canonical_name("а" * 256)
    except DocumentNameError as error:
        assert error.code == "name_too_long"
    else:
        raise AssertionError("expected name_too_long")


def test_upload_keeps_a_name_that_would_split_a_letter_at_the_limit():
    bundle = build()
    token = sign_in(bundle).json()["access_token"]
    uploaded = bundle.client.post(
        "/api/v1/documents",
        headers={**bearer(token), "Idempotency-Key": str(uuid4())},
        files={"file": (SPLIT_LETTER_NAME, LECTURE, "application/pdf")},
    )
    assert uploaded.status_code == 201
    assert uploaded.json()["name"] == SPLIT_LETTER_NAME
    assert uploaded.json()["name"] != NAIVE_BROKEN
    assert "\ufffd" not in uploaded.json()["name"]
