"""A photo replaces only this person's photo, and a bad file leaves the previous one."""

from urllib.parse import urlparse

import pytest

from domain.account.photo import MAX_PHOTO_BYTES
from tests.support import GIF, JPEG, PNG, WEBP, bearer, build, sign_in


def _upload(bundle, token, body, name="photo.bin"):
    return bundle.client.put(
        "/api/v1/user/avatar",
        headers=bearer(token),
        files={"file": (name, body, "application/octet-stream")},
    )


@pytest.mark.parametrize("body", [pytest.param(GIF, id="other-kind")])
def test_an_invalid_photo_is_refused(body):
    bundle = build()
    token = sign_in(bundle).json()["access_token"]
    _upload(bundle, token, JPEG)
    before = bundle.store.avatar_count()
    previous = bundle.client.get("/api/v1/user/profile", headers=bearer(token)).json()["avatar_url"]
    refused = _upload(bundle, token, body)
    assert refused.status_code in {413, 422}
    assert bundle.store.avatar_count() == before
    assert bundle.client.get("/api/v1/user/profile", headers=bearer(token)).json()["avatar_url"] == previous


@pytest.mark.parametrize("body", [JPEG, PNG, WEBP])
def test_an_allowed_photo_replaces_the_previous_one(body):
    bundle = build()
    token = sign_in(bundle).json()["access_token"]
    first = _upload(bundle, token, JPEG)
    second = _upload(bundle, token, body)
    assert second.status_code == 200
    previous = first.json()["avatar_url"]
    current = second.json()["avatar_url"]
    assert current != previous
    assert bundle.client.get(urlparse(previous).path).status_code == 404
    assert bundle.client.get(urlparse(current).path).content == body


def test_a_photo_larger_than_ten_megabytes_is_not_kept():
    test_an_invalid_photo_is_refused(b"\xff\xd8\xff" + b"\x00" * MAX_PHOTO_BYTES)


def test_removing_the_photo_leaves_the_profile_without_one():
    bundle = build()
    token = sign_in(bundle).json()["access_token"]
    uploaded = _upload(bundle, token, PNG)
    removed = bundle.client.delete("/api/v1/user/avatar", headers=bearer(token))
    assert removed.status_code == 200
    assert removed.json()["avatar_url"] is None
    assert bundle.client.get(urlparse(uploaded.json()["avatar_url"]).path).status_code == 404


def test_replacing_or_removing_a_photo_leaves_the_neighbour():
    bundle = build()
    token = sign_in(bundle).json()["access_token"]
    neighbour = sign_in(bundle, code="boris", subject="ya-boris", email="boris@yandex.ru", name="Борис").json()
    mine = _upload(bundle, token, JPEG).json()["avatar_url"]
    theirs = _upload(bundle, neighbour["access_token"], PNG).json()["avatar_url"]
    _upload(bundle, token, WEBP)
    assert bundle.client.get(urlparse(theirs).path).content == PNG
    assert bundle.client.get(urlparse(mine).path).status_code == 404
    bundle.client.delete("/api/v1/user/avatar", headers=bearer(token))
    assert bundle.client.get(urlparse(theirs).path).content == PNG

