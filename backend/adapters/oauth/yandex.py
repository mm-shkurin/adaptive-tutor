from urllib.parse import urlencode

import httpx

from domain.account.identity import ProviderIdentity
from usecase.account.errors import OAuthFailed


class YandexOAuthProvider:
    name = "yandex"

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, authorize_url: str, token_url: str, info_url: str, transport=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.authorize_url = authorize_url
        self.token_url = token_url
        self.info_url = info_url
        self.transport = transport

    def authorization_url(self, state: str) -> str:
        query = urlencode(
            {
                "response_type": "code",
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "state": state,
            }
        )
        return f"{self.authorize_url}?{query}"

    async def fetch_identity(self, code: str) -> ProviderIdentity:
        try:
            async with httpx.AsyncClient(timeout=10, transport=self.transport) as http:
                token = await self._token(http, code)
                return await self._identity(http, token)
        except httpx.HTTPError as error:
            raise OAuthFailed() from error

    async def _token(self, http: httpx.AsyncClient, code: str) -> str:
        answer = await http.post(
            self.token_url,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )
        if not answer.is_success:
            raise OAuthFailed()
        try:
            token = answer.json().get("access_token")
        except ValueError as error:
            raise OAuthFailed() from error
        if not token:
            raise OAuthFailed()
        return token

    async def _identity(self, http: httpx.AsyncClient, token: str) -> ProviderIdentity:
        answer = await http.get(self.info_url, headers={"Authorization": f"OAuth {token}"})
        if not answer.is_success:
            raise OAuthFailed()
        try:
            profile = answer.json()
        except ValueError as error:
            raise OAuthFailed() from error
        subject = profile.get("id")
        email = profile.get("default_email")
        if not subject or not isinstance(email, str) or not email:
            raise OAuthFailed()
        return ProviderIdentity(str(subject), email, _name(profile) or email.split("@", 1)[0])


def _name(profile: dict) -> str:
    for key in ("real_name", "display_name"):
        value = profile.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    parts = [profile.get("first_name"), profile.get("last_name")]
    pair = " ".join(part.strip() for part in parts if isinstance(part, str) and part.strip())
    if pair:
        return pair
    login = profile.get("login")
    if isinstance(login, str) and login.strip():
        return login.strip()
    return ""
