from dataclasses import dataclass
from datetime import datetime, timedelta
from secrets import token_urlsafe
from urllib.parse import urlencode

from usecase.account.errors import OAuthFailed, Unauthorized
from usecase.account.ports import AccountStore, OAuthCodes, OAuthProvider, TokenIssuer


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class SignIn:
    def __init__(
        self,
        provider: OAuthProvider,
        codes: OAuthCodes,
        accounts: AccountStore,
        tokens: TokenIssuer,
        clock,
        state_ttl: timedelta,
        handoff_ttl: timedelta,
        frontend_callback_url: str,
    ):
        self.provider = provider
        self.codes = codes
        self.accounts = accounts
        self.tokens = tokens
        self.clock = clock
        self.state_ttl = state_ttl
        self.handoff_ttl = handoff_ttl
        self.frontend_callback_url = frontend_callback_url

    async def start(self) -> tuple[str, str]:
        browser = token_urlsafe(32)
        state = token_urlsafe(32)
        expires_at = self.clock.now() + self.state_ttl
        await self.codes.mint_state(state, self.provider.name, browser, expires_at)
        return self.provider.authorization_url(state), browser

    async def callback(self, code: str, state: str, error: str) -> str:
        browser = await self.codes.take_state(state, self.provider.name, self.clock.now())
        if browser is None:
            return self._location(error="state_invalid")
        if _broken(code) or _broken(error) or error:
            return self._location(error="provider_failed")
        if not code:
            return self._location(error="code_missing")
        try:
            identity = await self.provider.fetch_identity(code)
        except OAuthFailed:
            return self._location(error="provider_failed")
        account = await self.accounts.get_or_create(identity, self.clock.now())
        handoff = token_urlsafe(32)
        expires_at = self.clock.now() + self.handoff_ttl
        await self.codes.mint_handoff(handoff, account.id, browser, expires_at)
        return self._location(code=handoff)

    async def exchange(self, code: str, browser: str) -> TokenPair:
        user_id = await self.codes.take_handoff(code, browser, self.clock.now())
        if user_id is None:
            raise Unauthorized()
        return self.tokens.issue(user_id)

    def _location(self, **params: str) -> str:
        base = self.frontend_callback_url
        separator = "&" if "?" in base else "?"
        location = f"{base}{separator}{urlencode(params)}"
        if "\r" in location or "\n" in location:
            return f"{base}{separator}{urlencode({'error': 'provider_failed'})}"
        return location


def _broken(value: str) -> bool:
    return "\r" in value or "\n" in value
