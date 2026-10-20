from urllib.parse import urlencode

from domain.account.identity import ProviderIdentity
from usecase.account.errors import OAuthFailed


class FakeOAuthProvider:
    """A Yandex stand-in for a stack with no client secret. The code names the person."""

    name = "yandex"

    def __init__(self, redirect_uri: str):
        self.redirect_uri = redirect_uri

    def authorization_url(self, state: str) -> str:
        return f"{self.redirect_uri}?{urlencode({'code': 'demo', 'state': state})}"

    async def fetch_identity(self, code: str) -> ProviderIdentity:
        if not code or code.startswith("refuse"):
            raise OAuthFailed()
        return ProviderIdentity(f"fake-{code}", f"{code}@example.test", code)
