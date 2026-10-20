from domain.account.account import Account
from usecase.account.errors import Unauthorized
from usecase.account.ports import AccountStore, Revocations, TokenIssuer
from usecase.account.sign_in import TokenPair


class SessionService:
    def __init__(self, accounts: AccountStore, tokens: TokenIssuer, revocations: Revocations):
        self.accounts = accounts
        self.tokens = tokens
        self.revocations = revocations

    async def caller(self, access_token: str | None) -> Account:
        claims = await self._live(access_token, "access")
        return await self._account(claims.user_id)

    async def refresh(self, refresh_token: str) -> TokenPair:
        claims = await self._live(refresh_token, "refresh")
        await self._account(claims.user_id)
        return TokenPair(self.tokens.issue_access(claims.user_id), refresh_token)

    async def logout(self, access_token: str | None, refresh_token: str | None) -> None:
        claims = self.tokens.read(access_token or "", "access")
        if claims is None:
            raise Unauthorized()
        await self.revocations.revoke(access_token or "", claims.expires_at)
        if not refresh_token:
            return
        refresh_claims = self.tokens.read(refresh_token, "refresh")
        if refresh_claims is not None:
            await self.revocations.revoke(refresh_token, refresh_claims.expires_at)

    async def _live(self, token: str | None, kind: str):
        if not token or await self.revocations.is_revoked(token):
            raise Unauthorized()
        claims = self.tokens.read(token, kind)
        if claims is None:
            raise Unauthorized()
        return claims

    async def _account(self, user_id) -> Account:
        account = await self.accounts.get(user_id)
        if account is None:
            raise Unauthorized()
        return account
