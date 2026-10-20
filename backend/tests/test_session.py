"""Sign-out kills one session. Delete kills the account and nothing next to it."""

from tests.support import JPEG, bearer, build, handoff, sign_in


def _pair(bundle, code, subject, email, name):
    issued = handoff(bundle, code, subject, email, name)
    body = bundle.client.post("/api/v1/auth/oauth/exchange", json={"code": issued}).json()
    return body["access_token"], body["refresh_token"]


def test_sign_out_revokes_the_session_and_a_second_sign_out_is_accepted():
    bundle = build()
    access, refresh = _pair(bundle, "ada", "ya-ada", "ada@yandex.ru", "Ада")
    first = bundle.client.post("/api/v1/auth/logout", headers=bearer(access), json={"refresh_token": refresh})
    assert first.status_code == 204
    assert bundle.client.get("/api/v1/user/profile", headers=bearer(access)).status_code == 401
    rename = bundle.client.patch("/api/v1/user/profile", headers=bearer(access), json={"name": "Другое"})
    assert rename.status_code == 401
    again = bundle.client.post("/api/v1/auth/logout", headers=bearer(access), json={"refresh_token": refresh})
    assert again.status_code == 204
    returned = sign_in(bundle, code="ada-2", subject="ya-ada", email="ada@yandex.ru", name="Ада")
    profile = bundle.client.get("/api/v1/user/profile", headers=bearer(returned.json()["access_token"])).json()
    assert profile["name"] == "Ада"
    assert bundle.store.count() == 1


def test_refresh_returns_a_new_access_token_and_the_same_refresh_token():
    bundle = build()
    access, refresh = _pair(bundle, "ada", "ya-ada", "ada@yandex.ru", "Ада")
    refreshed = bundle.client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert refreshed.status_code == 200
    body = refreshed.json()
    assert body["refresh_token"] == refresh
    assert body["access_token"] != access
    assert bundle.client.get("/api/v1/user/profile", headers=bearer(body["access_token"])).status_code == 200


def test_a_revoked_session_cannot_refresh_or_read():
    bundle = build()
    access, refresh = _pair(bundle, "ada", "ya-ada", "ada@yandex.ru", "Ада")
    bundle.client.post("/api/v1/auth/logout", headers=bearer(access), json={"refresh_token": refresh})
    refused_refresh = bundle.client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    refused_profile = bundle.client.get("/api/v1/user/profile", headers=bearer(access))
    assert refused_refresh.status_code == 401
    assert refused_profile.status_code == 401
    assert access not in refused_refresh.text and access not in refused_profile.text
    assert refresh not in refused_refresh.text and refresh not in refused_profile.text


def test_an_access_token_presented_as_a_refresh_token_is_refused():
    bundle = build()
    access, _refresh = _pair(bundle, "ada", "ya-ada", "ada@yandex.ru", "Ада")
    refused = bundle.client.post("/api/v1/auth/refresh", json={"refresh_token": access})
    assert refused.status_code == 401
    assert bundle.client.get("/api/v1/user/profile", headers=bearer(access)).status_code == 200


def test_delete_removes_only_this_account_and_the_same_yandex_identity_is_new():
    bundle = build()
    access, _refresh = _pair(bundle, "ada", "ya-ada", "ada@yandex.ru", "Ада")
    old_id = bundle.client.get("/api/v1/user/profile", headers=bearer(access)).json()["id"]
    neighbour = sign_in(bundle, code="boris", subject="ya-boris", email="boris@yandex.ru", name="Борис").json()
    deleted = bundle.client.delete("/api/v1/user", headers=bearer(access))
    assert deleted.status_code == 204
    assert bundle.client.get("/api/v1/user/profile", headers=bearer(access)).status_code == 401
    assert bundle.client.get("/api/v1/user/profile", headers=bearer(neighbour["access_token"])).json()["name"] == "Борис"
    unknown = bundle.client.get("/api/v1/user/profile", headers=bearer("not-a-token"))
    former = bundle.client.get("/api/v1/user/profile", headers=bearer(access))
    assert former.status_code == unknown.status_code == 401
    assert former.json() == unknown.json()
    assert "ada@yandex.ru" not in former.text and access not in former.text
    again = sign_in(bundle, code="ada-3", subject="ya-ada", email="ada@yandex.ru", name="Ада")
    assert again.json()["access_token"]
    new_profile = bundle.client.get("/api/v1/user/profile", headers=bearer(again.json()["access_token"])).json()
    assert new_profile["id"] != old_id
    assert new_profile["email"] == "ada@yandex.ru"
    assert bundle.store.count() == 2


def test_a_second_delete_matches_an_unknown_session_and_spares_the_neighbour():
    bundle = build()
    access, _refresh = _pair(bundle, "ada", "ya-ada", "ada@yandex.ru", "Ада")
    sign_in(bundle, code="boris", subject="ya-boris", email="boris@yandex.ru", name="Борис")
    assert bundle.client.delete("/api/v1/user", headers=bearer(access)).status_code == 204
    unknown = bundle.client.delete("/api/v1/user", headers=bearer("not-a-token"))
    second = bundle.client.delete("/api/v1/user", headers=bearer(access))
    assert second.status_code == unknown.status_code == 401
    assert second.json() == unknown.json()
    assert bundle.store.count() == 1


def test_a_delete_with_no_session_removes_no_account():
    bundle = build()
    sign_in(bundle)
    sign_in(bundle, code="boris", subject="ya-boris", email="boris@yandex.ru", name="Борис")
    refused = bundle.client.delete("/api/v1/user")
    assert refused.status_code == 401
    assert bundle.store.count() == 2


def test_a_deleted_session_matches_an_unknown_one_on_writes_and_refresh():
    bundle = build()
    access, refresh = _pair(bundle, "ada", "ya-ada", "ada@yandex.ru", "Ада")
    bundle.client.put("/api/v1/user/avatar", headers=bearer(access), files={"file": ("a.jpg", JPEG, "image/jpeg")})
    bundle.client.delete("/api/v1/user", headers=bearer(access))
    calls = [
        ("patch", "/api/v1/user/profile", {"json": {"name": "Новое"}}),
        ("put", "/api/v1/user/avatar", {"files": {"file": ("a.jpg", JPEG, "image/jpeg")}}),
        ("delete", "/api/v1/user/avatar", {}),
    ]
    for method, path, extra in calls:
        former = getattr(bundle.client, method)(path, headers=bearer(access), **extra)
        unknown = getattr(bundle.client, method)(path, headers=bearer("not-a-token"), **extra)
        assert former.status_code == unknown.status_code == 401
        assert former.json() == unknown.json()
    former_refresh = bundle.client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    unknown_refresh = bundle.client.post("/api/v1/auth/refresh", json={"refresh_token": "not-a-token"})
    assert former_refresh.status_code == unknown_refresh.status_code == 401
    assert former_refresh.json() == unknown_refresh.json()
    assert bundle.store.count() == 0


def test_a_failure_never_echoes_the_token_or_the_email():
    bundle = build()
    access, _refresh = _pair(bundle, "ada", "ya-ada", "ada@yandex.ru", "Ада")
    missed = bundle.client.post("/api/v1/auth/oauth/exchange", json={"code": "missing"})
    renamed = bundle.client.patch("/api/v1/user/profile", headers=bearer(access), json={"name": "а" * 61})
    photo = bundle.client.put(
        "/api/v1/user/avatar",
        headers=bearer(access),
        files={"file": ("a.gif", b"GIF89a", "image/gif")},
    )
    deleted = bundle.client.delete("/api/v1/user")
    for response in (missed, renamed, photo, deleted):
        assert "ada@yandex.ru" not in response.text
        assert access not in response.text
