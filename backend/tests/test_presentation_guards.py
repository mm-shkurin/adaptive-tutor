from uuid import uuid4

import pytest

from tests.presentation_flow import MISSING, PROGRESS_MISSING, create
from tests.quiz_flow import ada, neighbour
from tests.support import JPEG, bearer, build

@pytest.mark.parametrize(
    "call",
    [
        lambda b: b.client.post("/api/v1/presentations", json={"title": "x"}),
        lambda b: b.client.get(f"/api/v1/presentations/{uuid4()}"),
        lambda b: b.client.patch(f"/api/v1/presentations/{uuid4()}", json={"title": "x"}),
        lambda b: b.client.post(
            f"/api/v1/presentations/{uuid4()}/slides",
            headers={"Idempotency-Key": "k"},
            files=[("images", ("a.jpg", JPEG, "image/jpeg"))],
        ),
        lambda b: b.client.delete(f"/api/v1/presentations/{uuid4()}/slides/{uuid4()}"),
        lambda b: b.client.post(
            f"/api/v1/presentations/{uuid4()}/index",
            headers={"Idempotency-Key": "k"},
        ),
        lambda b: b.client.delete(f"/api/v1/presentations/{uuid4()}"),
        lambda b: b.client.get("/api/v1/progress"),
    ],
)
def test_unsigned_call_is_refused(call):
    bundle = build()
    response = call(bundle)
    body = response.json()
    assert response.status_code == 404
    assert body == (MISSING if "progress" not in response.request.url.path else PROGRESS_MISSING)
    assert bundle.presentations.count() == 0


def test_neighbour_presentation_looks_absent():
    bundle = build()
    ada_token, _ = ada(bundle)
    grace_token, _ = neighbour(bundle)
    created = create(bundle, grace_token, "secret")
    presentation_id = created.json()["id"]
    before = bundle.client.get(
        f"/api/v1/presentations/{presentation_id}",
        headers=bearer(grace_token),
    ).json()
    for call in (
        lambda: bundle.client.get(f"/api/v1/presentations/{presentation_id}", headers=bearer(ada_token)),
        lambda: bundle.client.patch(
            f"/api/v1/presentations/{presentation_id}",
            headers=bearer(ada_token),
            json={"title": "stolen"},
        ),
        lambda: bundle.client.post(
            f"/api/v1/presentations/{presentation_id}/index",
            headers={**bearer(ada_token), "Idempotency-Key": "n1"},
        ),
        lambda: bundle.client.delete(f"/api/v1/presentations/{presentation_id}", headers=bearer(ada_token)),
    ):
        response = call()
        assert response.status_code == 404
        assert response.json() == MISSING
    after = bundle.client.get(
        f"/api/v1/presentations/{presentation_id}",
        headers=bearer(grace_token),
    ).json()
    assert after == before


def test_progress_without_session_matches_absent():
    bundle = build()
    response = bundle.client.get("/api/v1/progress")
    assert response.status_code == 404
    assert response.json() == PROGRESS_MISSING