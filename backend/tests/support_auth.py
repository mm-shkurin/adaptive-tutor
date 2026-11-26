from urllib.parse import parse_qs, urlparse

from domain.account.identity import ProviderIdentity


def allow(bundle, code: str, subject: str, email: str, name: str) -> None:
    bundle.provider.by_code[code] = ProviderIdentity(subject, email, name)


def query(url: str) -> dict:
    return parse_qs(urlparse(url).query)


def bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def handoff(bundle, code: str, subject: str, email: str, name: str) -> str:
    allow(bundle, code, subject, email, name)
    started = bundle.client.get("/api/v1/auth/oauth/yandex/start", follow_redirects=False)
    state = query(started.headers["location"])["state"][0]
    back = bundle.client.get(
        "/api/v1/auth/oauth/yandex/callback",
        params={"code": code, "state": state},
        follow_redirects=False,
    )
    return query(back.headers["location"])["code"][0]


def sign_in(bundle, code="ada", subject="ya-ada", email="ada@yandex.ru", name="Ада"):
    issued = handoff(bundle, code, subject, email, name)
    return bundle.client.post("/api/v1/auth/oauth/exchange", json={"code": issued})


def auth_profile(bundle, token: str):
    return bundle.client.get("/api/v1/user/profile", headers=bearer(token))
