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


def test_mass_assignment_cannot_set_status_or_piece_count_on_create():
    bundle = build()
    access, _ = ada(bundle)
    created = bundle.client.post(
        "/api/v1/presentations",
        headers=bearer(access),
        json={"title": "LinAlg", "status": "ready", "piece_count": 9},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["status"] == "draft"
    assert body["piece_count"] is None


def test_virus_error_body_does_not_disclose_path_or_bytes():
    bundle = build()
    access, _ = ada(bundle)
    bundle.virus.set_outcome("finds_virus")
    presentation_id = create(bundle, access).json()["id"]
    response = bundle.client.post(
        f"/api/v1/presentations/{presentation_id}/slides",
        headers={**bearer(access), "Idempotency-Key": "v1"},
        files=[("images", ("C:\\secrets\\slide.jpg", JPEG, "image/jpeg"))],
    )
    assert response.status_code == 400
    payload = response.json()
    text = str(payload)
    assert payload == {"code": "virus_detected", "message": "Virus detected"}
    assert "C:\\secrets" not in text
    assert "\\xff" not in text
    assert "Traceback" not in text


def test_neighbour_slides_and_delete_slide_look_absent():
    bundle = build()
    ada_token, _ = ada(bundle)
    grace_token, _ = neighbour(bundle)
    presentation_id = create(bundle, grace_token, "secret").json()["id"]
    slide_id = bundle.client.post(
        f"/api/v1/presentations/{presentation_id}/slides",
        headers={**bearer(grace_token), "Idempotency-Key": "g1"},
        files=[("images", ("a.jpg", JPEG, "image/jpeg"))],
    ).json()["slides"][0]["id"]
    before = bundle.client.get(
        f"/api/v1/presentations/{presentation_id}",
        headers=bearer(grace_token),
    ).json()
    for call in (
        lambda: bundle.client.post(
            f"/api/v1/presentations/{presentation_id}/slides",
            headers={**bearer(ada_token), "Idempotency-Key": "steal"},
            files=[("images", ("b.jpg", JPEG, "image/jpeg"))],
        ),
        lambda: bundle.client.delete(
            f"/api/v1/presentations/{presentation_id}/slides/{slide_id}",
            headers=bearer(ada_token),
        ),
    ):
        response = call()
        assert response.status_code == 404
        assert response.json() == MISSING
    after = bundle.client.get(
        f"/api/v1/presentations/{presentation_id}",
        headers=bearer(grace_token),
    ).json()
    assert after == before