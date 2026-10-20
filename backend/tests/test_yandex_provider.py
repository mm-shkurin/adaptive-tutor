"""The Yandex client talks to the provider once and does not invent an identity."""

import asyncio

import httpx

from adapters.oauth.yandex import YandexOAuthProvider
from usecase.account.errors import OAuthFailed


def _provider(handler) -> YandexOAuthProvider:
    return YandexOAuthProvider(
        "client-id-client-id-client-id-1",
        "client-secret-client-secret-secret",
        "http://localhost:8000/api/v1/auth/oauth/yandex/callback",
        "https://oauth.yandex.ru/authorize",
        "https://oauth.yandex.ru/token",
        "https://login.yandex.ru/info",
        transport=httpx.MockTransport(handler),
    )


def test_the_authorisation_url_uses_the_configured_client():
    provider = _provider(lambda request: httpx.Response(500))
    url = provider.authorization_url("state-1")
    assert url.startswith("https://oauth.yandex.ru/authorize?")
    assert "client-id-client-id-client-id-1" in url
    assert "state-1" in url


def test_a_server_error_is_one_call_and_not_an_identity():
    calls = {"n": 0}

    def handler(_request):
        calls["n"] += 1
        return httpx.Response(500, text="down")

    with pytest_raises():
        asyncio.run(_provider(handler).fetch_identity("code"))
    assert calls["n"] == 1


def test_a_timeout_finishes_as_a_failure():
    def handler(_request):
        raise httpx.ConnectTimeout("timed out")

    with pytest_raises():
        asyncio.run(_provider(handler).fetch_identity("code"))


def test_an_unreadable_body_is_a_failure():
    def handler(request):
        if request.url.path.endswith("/token"):
            return httpx.Response(200, text="not-json")
        return httpx.Response(200, json={"id": "1", "default_email": "ada@yandex.ru", "real_name": "Ада"})

    with pytest_raises():
        asyncio.run(_provider(handler).fetch_identity("code"))


def test_a_readable_profile_becomes_an_identity():
    def handler(request):
        if str(request.url).endswith("/token"):
            return httpx.Response(200, json={"access_token": "provider-token"})
        return httpx.Response(200, json={"id": 7, "default_email": "ada@yandex.ru", "real_name": "Ада"})

    identity = asyncio.run(_provider(handler).fetch_identity("code"))
    assert identity.subject == "7"
    assert identity.email == "ada@yandex.ru"
    assert identity.name == "Ада"


def pytest_raises():
    import pytest

    return pytest.raises(OAuthFailed)
