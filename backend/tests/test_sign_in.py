"""Yandex sign-in opens one account and refuses a code that is not this browser's."""

from fastapi.testclient import TestClient

from tests.support import CREATED, auth_profile, build, handoff, query, sign_in
from usecase.account.errors import OAuthFailed


def test_yandex_confirmation_opens_one_session():
    bundle = build()
    exchanged = sign_in(bundle)
    assert exchanged.status_code == 200
    body = exchanged.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]
    assert bundle.store.count() == 1
    assert bundle.provider.calls == 1
    profile = auth_profile(bundle, body["access_token"]).json()
    assert profile["email"] == "ada@yandex.ru"
    assert profile["name"] == "Ада"
    assert profile["created_at"] == CREATED


def test_the_same_return_played_twice_opens_one_account():
    bundle = build()
    issued = handoff(bundle, "ada", "ya-ada", "ada@yandex.ru", "Ада")
    first = bundle.client.post("/api/v1/auth/oauth/exchange", json={"code": issued})
    second = bundle.client.post("/api/v1/auth/oauth/exchange", json={"code": issued})
    assert first.status_code == 200
    assert second.status_code == 401
    assert "access_token" not in second.json()
    assert bundle.store.count() == 1


def test_an_expired_return_opens_no_account():
    bundle = build(state_ttl=10)
    started = bundle.client.get("/api/v1/auth/oauth/yandex/start", follow_redirects=False)
    state = query(started.headers["location"])["state"][0]
    bundle.clock.advance(10)
    back = bundle.client.get(
        "/api/v1/auth/oauth/yandex/callback",
        params={"code": "ada", "state": state},
        follow_redirects=False,
    )
    assert query(back.headers["location"])["error"] == ["state_invalid"]
    assert bundle.store.count() == 0
    assert bundle.provider.calls == 0


def test_a_foreign_unknown_and_expired_code_are_the_same_refusal():
    bundle = build(handoff_ttl=30)
    issued = handoff(bundle, "ada", "ya-ada", "ada@yandex.ru", "Ада")
    stranger = TestClient(bundle.client.app, raise_server_exceptions=False)
    foreign = stranger.post("/api/v1/auth/oauth/exchange", json={"code": issued})
    unknown = bundle.client.post("/api/v1/auth/oauth/exchange", json={"code": "never-issued"})
    expired_code = handoff(bundle, "ada", "ya-ada", "ada@yandex.ru", "Ада")
    bundle.clock.advance(30)
    expired = bundle.client.post("/api/v1/auth/oauth/exchange", json={"code": expired_code})
    assert foreign.status_code == unknown.status_code == expired.status_code == 401
    assert foreign.json() == unknown.json() == expired.json()
    assert bundle.store.count() == 1
    assert "ada@yandex.ru" not in foreign.text


def test_exchange_cannot_set_id_email_or_role():
    bundle = build()
    issued = handoff(bundle, "ada", "ya-ada", "ada@yandex.ru", "Ада")
    exchanged = bundle.client.post(
        "/api/v1/auth/oauth/exchange",
        json={"code": issued, "id": "11111111-1111-1111-1111-111111111111", "email": "other@evil.test", "role": "admin"},
    )
    profile = auth_profile(bundle, exchanged.json()["access_token"]).json()
    assert profile["id"] != "11111111-1111-1111-1111-111111111111"
    assert profile["email"] == "ada@yandex.ru"
    assert "role" not in profile


def test_provider_failure_leaves_the_guest_signed_out():
    bundle = build()
    bundle.provider.by_code["ada"] = OAuthFailed()
    started = bundle.client.get("/api/v1/auth/oauth/yandex/start", follow_redirects=False)
    state = query(started.headers["location"])["state"][0]
    back = bundle.client.get(
        "/api/v1/auth/oauth/yandex/callback",
        params={"code": "ada", "state": state},
        follow_redirects=False,
    )
    assert query(back.headers["location"])["error"] == ["provider_failed"]
    assert "code" not in query(back.headers["location"])
    assert bundle.store.count() == 0
    assert bundle.provider.calls == 1


def test_a_failed_session_then_a_retry_is_still_one_account():
    bundle = build()

    class Once:
        def __init__(self, inner):
            self.inner = inner
            self.failed = False

        def issue(self, user_id):
            if not self.failed:
                self.failed = True
                raise RuntimeError("could not sign")
            return self.inner.issue(user_id)

    bundle.client.app.state.ctx.sign_in.tokens = Once(bundle.client.app.state.ctx.sign_in.tokens)
    issued = handoff(bundle, "ada", "ya-ada", "ada@yandex.ru", "Ада")
    failed = bundle.client.post("/api/v1/auth/oauth/exchange", json={"code": issued})
    assert failed.status_code == 500
    assert "ada@yandex.ru" not in failed.text
    assert "could not sign" not in failed.text
    again = sign_in(bundle, code="ada-2", subject="ya-ada", email="ada@yandex.ru", name="Ада")
    assert again.status_code == 200
    assert bundle.store.count() == 1


def test_a_return_cannot_break_the_redirect():
    bundle = build()
    started = bundle.client.get("/api/v1/auth/oauth/yandex/start", follow_redirects=False)
    state = query(started.headers["location"])["state"][0]
    broken_code = bundle.client.get(
        "/api/v1/auth/oauth/yandex/callback",
        params={"code": "ab\r\nX-Injected: 1", "state": state},
        follow_redirects=False,
    )
    started_again = bundle.client.get("/api/v1/auth/oauth/yandex/start", follow_redirects=False)
    state_again = query(started_again.headers["location"])["state"][0]
    broken_error = bundle.client.get(
        "/api/v1/auth/oauth/yandex/callback",
        params={"error": "no\r\nSet-Cookie: evil", "state": state_again},
        follow_redirects=False,
    )
    for response in (broken_code, broken_error):
        location = response.headers["location"]
        assert "\r" not in location and "\n" not in location
        assert "x-injected" not in {name.lower() for name in response.headers}
        assert query(location)["error"] == ["provider_failed"]
    assert bundle.store.count() == 0
