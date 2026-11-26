from tests.presentation_flow import add_image, create, index, material, token
from tests.support import bearer, build


def test_creating_a_draft_stores_an_empty_presentation():
    bundle = build()
    access = token(bundle)
    created = create(bundle, access, "LinAlg")
    assert created.status_code == 201
    body = created.json()
    assert body["title"] == "LinAlg"
    assert body["status"] == "draft"
    assert body["slide_count"] == 0
    assert body["slides"] == []
    read_back = bundle.client.get(
        f"/api/v1/presentations/{body['id']}", headers=bearer(access)
    ).json()
    assert read_back == body
    materials = material(bundle, access)["documents"][0]
    assert materials["kind"] == "presentation"
    assert materials["name"] == "LinAlg"
    assert materials["status"] == "draft"
    assert materials["id"] == body["id"]


def test_omitted_title_becomes_the_default_draft_title():
    bundle = build()
    access = token(bundle)
    created = create(bundle, access, None)
    assert created.status_code == 201
    body = created.json()
    assert body["title"] == "Новая презентация"
    assert body["status"] == "draft"


def test_oversized_image_is_refused():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    huge = b"\xff\xd8\xff" + b"\x00" * (52_428_801 - 3)
    response = bundle.client.post(
        f"/api/v1/presentations/{presentation_id}/slides",
        headers={**bearer(access), "Idempotency-Key": "big"},
        files=[("images", ("huge.jpg", huge, "image/jpeg"))],
    )
    assert response.status_code == 400
    assert response.json() == {"code": "file_too_large", "message": "File is too large"}
    assert bundle.client.get(
        f"/api/v1/presentations/{presentation_id}", headers=bearer(access)
    ).json()["slide_count"] == 0


def test_virus_on_image_refuses_the_add():
    bundle = build()
    access = token(bundle)
    bundle.virus.set_outcome("finds_virus")
    presentation_id = create(bundle, access).json()["id"]
    response = add_image(bundle, access, presentation_id)
    assert response.status_code == 400
    assert response.json() == {"code": "virus_detected", "message": "Virus detected"}
    assert bundle.client.get(
        f"/api/v1/presentations/{presentation_id}", headers=bearer(access)
    ).json()["slide_count"] == 0


def test_same_idempotency_key_does_not_duplicate_slides():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    first = add_image(bundle, access, presentation_id, key="same-key")
    second = add_image(bundle, access, presentation_id, key="same-key")
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
    assert first.json()["slide_count"] == 1


def test_adding_slides_without_idempotency_key_is_refused():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    response = bundle.client.post(
        f"/api/v1/presentations/{presentation_id}/slides",
        headers=bearer(access),
        files=[("images", ("slide.jpg", b"\xff\xd8\xff\xd9", "image/jpeg"))],
    )
    assert response.status_code == 422
    assert (
        bundle.client.get(f"/api/v1/presentations/{presentation_id}", headers=bearer(access)).json()[
            "slide_count"
        ]
        == 0
    )


def test_index_with_zero_slides_is_refused():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    response = index(bundle, access, presentation_id)
    assert response.status_code == 400
    assert response.json() == {"code": "no_slides", "message": "Presentation has no slides"}
    assert bundle.client.get(
        f"/api/v1/presentations/{presentation_id}", headers=bearer(access)
    ).json()["status"] == "draft"


def test_more_than_forty_slides_cannot_be_added():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    for slide_index in range(40):
        added = add_image(bundle, access, presentation_id, key=f"k-{slide_index}")
        assert added.status_code == 200
    refused = add_image(bundle, access, presentation_id, key="k-40")
    assert refused.status_code == 400
    assert refused.json() == {"code": "slide_limit", "message": "More than 40 slides"}
    assert (
        bundle.client.get(f"/api/v1/presentations/{presentation_id}", headers=bearer(access)).json()[
            "slide_count"
        ]
        == 40
    )
