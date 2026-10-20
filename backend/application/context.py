import os
from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from adapters.cache.redis_oauth import RedisOAuthStore
from adapters.cache.redis_revocations import RedisRevocations
from adapters.oauth.fake import FakeOAuthProvider
from adapters.oauth.yandex import YandexOAuthProvider
from adapters.persistence.account_store import PostgresAccountStore
from adapters.tokens.jwt_tokens import JwtTokens
from application.settings import Settings, load_settings
from usecase.account.profile import ProfileService
from usecase.account.session import SessionService
from usecase.account.sign_in import SignIn


@dataclass
class RuntimeConfig:
    state_ttl: timedelta
    cors_origins: tuple[str, ...]


@dataclass
class AppContext:
    config: RuntimeConfig
    sign_in: SignIn
    session: SessionService
    profile: ProfileService
    accounts: object


def build_production_context(env=None) -> AppContext:
    settings = load_settings(os.environ if env is None else env)
    return _context(settings)


def _context(settings: Settings) -> AppContext:
    from redis.asyncio import Redis

    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    accounts = PostgresAccountStore(sessions)
    redis = Redis.from_url(settings.redis_url)
    tokens = JwtTokens(
        settings.jwt_access_secret,
        settings.jwt_refresh_secret,
        settings.access_ttl,
        settings.refresh_ttl,
    )
    provider = _provider(settings)
    return AppContext(
        config=RuntimeConfig(settings.state_ttl, settings.cors_origins),
        sign_in=SignIn(
            provider,
            RedisOAuthStore(redis),
            accounts,
            tokens,
            _WallClock(),
            settings.state_ttl,
            settings.handoff_ttl,
            settings.frontend_callback_url,
        ),
        session=SessionService(accounts, tokens, RedisRevocations(redis)),
        profile=ProfileService(accounts, settings.public_base_url),
        accounts=accounts,
    )


def _provider(settings: Settings):
    if settings.oauth_provider == "fake":
        return FakeOAuthProvider(settings.yandex_redirect_uri)
    return YandexOAuthProvider(
        settings.yandex_client_id,
        settings.yandex_client_secret,
        settings.yandex_redirect_uri,
        settings.yandex_authorize_url,
        settings.yandex_token_url,
        settings.yandex_info_url,
    )


class _WallClock:
    def now(self):
        from datetime import datetime, timezone

        return datetime.now(timezone.utc)
