"""The signed-in person reads and renames only their own profile."""

import pytest

from tests.support import CREATED, JPEG, auth_profile, bearer, build, sign_in


def _person(name="Ада", code="ada", subject="ya-ada"):
    bundle = build()
    token = sign_in(bundle, code=code, subject=subject, name=name).json()["access_token"]
    return bundle, token


def test_the_signed_in_person_reads_their_profile():
    bundle, token = _person()
    uploaded = bundle.client.put(
        "/api/v1/user/avatar",
        headers=bearer(token),
        files={"file": ("a.jpg", JPEG, "image/jpeg")},
    )
    profile = auth_profile(bundle, token)
    assert profile.status_code == 200
    body = profile.json()
    assert body["name"] == "Ада"
    assert body["email"] == "ada@yandex.ru"
    assert body["created_at"] == CREATED
    assert body["avatar_url"] == uploaded.json()["avatar_url"]
    assert set(body) == {"id", "name", "email", "avatar_url", "created_at"}


def test_sixty_cyrillic_letters_round_trip():
    bundle, token = _person()
    name = "я" * 60
    saved = bundle.client.patch("/api/v1/user/profile", headers=bearer(token), json={"name": name})
    assert saved.status_code == 200
    assert saved.json()["name"] == name
    assert auth_profile(bundle, token).json()["name"] == name


@pytest.mark.parametrize(
    "payload",
    [{"name": "а" * 61}, {"name": "   "}, {"name": None}, {}],
)
def test_an_invalid_name_is_refused(payload):
    bundle, token = _person()
    bundle.client.put(
        "/api/v1/user/avatar",
        headers=bearer(token),
        files={"file": ("a.jpg", JPEG, "image/jpeg")},
    )
    before = auth_profile(bundle, token).json()
    refused = bundle.client.patch("/api/v1/user/profile", headers=bearer(token), json=payload)
    assert refused.status_code == 422
    after = auth_profile(bundle, token).json()
    assert after["name"] == before["name"]
    assert after["avatar_url"] == before["avatar_url"]


def test_a_name_that_would_split_a_letter_is_not_stored_broken():
    bundle, token = _person()
    broken = ("я" * 59) + "е\u0301"
    refused = bundle.client.patch("/api/v1/user/profile", headers=bearer(token), json={"name": broken})
    assert refused.status_code == 422
    assert auth_profile(bundle, token).json()["name"] == "Ада"
    assert "\ufffd" not in auth_profile(bundle, token).text


def test_an_empty_name_restores_the_yandex_name():
    bundle, token = _person()
    bundle.client.patch("/api/v1/user/profile", headers=bearer(token), json={"name": "Своё"})
    bundle.client.put(
        "/api/v1/user/avatar",
        headers=bearer(token),
        files={"file": ("a.jpg", JPEG, "image/jpeg")},
    )
    before = auth_profile(bundle, token).json()["avatar_url"]
    restored = bundle.client.patch("/api/v1/user/profile", headers=bearer(token), json={"name": ""})
    assert restored.status_code == 200
    assert restored.json()["name"] == "Ада"
    assert restored.json()["avatar_url"] == before


def test_sixty_characters_stay_and_email_and_date_stay():
    bundle, token = _person()
    bundle.client.put(
        "/api/v1/user/avatar",
        headers=bearer(token),
        files={"file": ("a.jpg", JPEG, "image/jpeg")},
    )
    before = auth_profile(bundle, token).json()
    name = "а" * 60
    saved = bundle.client.patch("/api/v1/user/profile", headers=bearer(token), json={"name": name})
    assert saved.json()["name"] == name
    assert saved.json()["email"] == before["email"]
    assert saved.json()["created_at"] == before["created_at"]
    assert saved.json()["avatar_url"] == before["avatar_url"]


def test_two_saves_leave_the_last_accepted_name():
    bundle, token = _person()
    bundle.client.patch("/api/v1/user/profile", headers=bearer(token), json={"name": "Альфа"})
    bundle.client.patch("/api/v1/user/profile", headers=bearer(token), json={"name": "Бета"})
    body = auth_profile(bundle, token).json()
    assert body["name"] == "Бета"
    assert body["name"].count("Бета") == 1


def test_a_hostile_name_stays_text():
    bundle, token = _person()
    neighbour = sign_in(bundle, code="boris", subject="ya-boris", email="boris@yandex.ru", name="Борис").json()
    hostile = "'; DROP TABLE accounts;-- <script>alert(1)</script>"
    saved = bundle.client.patch("/api/v1/user/profile", headers=bearer(token), json={"name": hostile})
    assert saved.status_code == 200
    assert saved.json()["name"] == hostile
    assert saved.json()["email"] == "ada@yandex.ru"
    assert auth_profile(bundle, neighbour["access_token"]).json()["name"] == "Борис"


def test_a_rename_cannot_write_email_date_or_role():
    bundle, token = _person()
    before = auth_profile(bundle, token).json()
    refused = bundle.client.patch(
        "/api/v1/user/profile",
        headers=bearer(token),
        json={
            "name": "Новое",
            "email": "other@evil.test",
            "created_at": "2000-01-01T00:00:00Z",
            "role": "admin",
            "id": "11111111-1111-1111-1111-111111111111",
            "owner": "other",
            "avatar_url": "http://evil.test/a.png",
        },
    )
    assert refused.status_code == 422
    after = auth_profile(bundle, token).json()
    assert after == before
    assert "role" not in after
