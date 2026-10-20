from urllib.parse import parse_qs, urlparse
from uuid import uuid4

import httpx

from clients.application.http_result import HttpResult, read_result
from domain.account.identity import ProviderIdentity


class ScriptedProvider:
    name = "yandex"

    def __init__(self):
        self.by_code = {}

    def allow(self, code: str, email: str, name: str) -> None:
        self.by_code[code] = ProviderIdentity(f"fake-{code}", email, name)

    def authorization_url(self, state: str) -> str:
        return f"https://oauth.yandex.ru/authorize?state={state}"

    async def fetch_identity(self, code: str) -> ProviderIdentity:
        return self.by_code[code]


class SessionClient:
    def __init__(self, base_url: str, provider: ScriptedProvider):
        self.provider = provider
        self.http = httpx.Client(base_url=base_url, timeout=10, follow_redirects=False)

    def open_account(self, email: str, name: str) -> HttpResult:
        self.http.cookies.clear()
        code = uuid4().hex
        self.provider.allow(code, email, name)
        started = self.http.get("/api/v1/auth/oauth/yandex/start")
        if started.status_code != 302:
            return read_result(started)
        state = parse_qs(urlparse(started.headers["location"]).query)["state"][0]
        back = self.http.get("/api/v1/auth/oauth/yandex/callback", params={"code": code, "state": state})
        if back.status_code != 302:
            return read_result(back)
        handoff = parse_qs(urlparse(back.headers["location"]).query).get("code", [""])[0]
        exchanged = self.http.post("/api/v1/auth/oauth/exchange", json={"code": handoff})
        return read_result(exchanged)

    def close(self) -> None:
        self.http.close()
