from dataclasses import dataclass
from datetime import timedelta


class StartupError(RuntimeError):
    """The process must stop before it accepts anyone."""


@dataclass(frozen=True)
class Settings:
    database_url: str
    redis_url: str
    jwt_access_secret: str
    jwt_refresh_secret: str
    access_ttl: timedelta
    refresh_ttl: timedelta
    oauth_provider: str
    frontend_callback_url: str
    public_base_url: str
    state_ttl: timedelta
    handoff_ttl: timedelta
    cors_origins: tuple[str, ...]
    yandex_client_id: str
    yandex_client_secret: str
    yandex_redirect_uri: str
    yandex_authorize_url: str
    yandex_token_url: str
    yandex_info_url: str


def load_settings(env) -> Settings:
    provider = _text(env, "OAUTH_PROVIDER", "yandex")
    if provider not in {"yandex", "fake"}:
        raise StartupError("OAUTH_PROVIDER is unset")
    client_id = _text(env, "YANDEX_CLIENT_ID")
    client_secret = _text(env, "YANDEX_CLIENT_SECRET")
    if provider == "yandex" and (not client_id or not client_secret):
        raise StartupError("Yandex client settings are unset")
    return Settings(
        database_url=_required(env, "DATABASE_URL"),
        redis_url=_required(env, "REDIS_URL"),
        jwt_access_secret=_required(env, "JWT_ACCESS_SECRET"),
        jwt_refresh_secret=_required(env, "JWT_REFRESH_SECRET"),
        access_ttl=timedelta(minutes=_int(env, "ACCESS_TOKEN_EXPIRE_MINUTES", 60)),
        refresh_ttl=timedelta(minutes=_int(env, "REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 30)),
        oauth_provider=provider,
        frontend_callback_url=_text(env, "OAUTH_FRONTEND_CALLBACK_URL", "http://localhost:5173/auth/callback"),
        public_base_url=_text(env, "PUBLIC_BASE_URL", "http://localhost:8000"),
        state_ttl=timedelta(seconds=_int(env, "OAUTH_STATE_TTL_SECONDS", 600)),
        handoff_ttl=timedelta(seconds=_int(env, "OAUTH_HANDOFF_TTL_SECONDS", 120)),
        cors_origins=tuple(part.strip() for part in _text(env, "CORS_ORIGINS", "http://localhost:5173").split(",") if part.strip()),
        yandex_client_id=client_id,
        yandex_client_secret=client_secret,
        yandex_redirect_uri=_text(env, "YANDEX_REDIRECT_URI", "http://localhost:8000/api/v1/auth/oauth/yandex/callback"),
        yandex_authorize_url=_text(env, "YANDEX_AUTHORIZE_URL", "https://oauth.yandex.ru/authorize"),
        yandex_token_url=_text(env, "YANDEX_TOKEN_URL", "https://oauth.yandex.ru/token"),
        yandex_info_url=_text(env, "YANDEX_INFO_URL", "https://login.yandex.ru/info"),
    )


def _required(env, name: str) -> str:
    value = _text(env, name)
    if not value:
        raise StartupError(f"{name} is unset")
    return value


def _text(env, name: str, default: str = "") -> str:
    value = env.get(name)
    if value is None:
        return default
    return str(value).strip()


def _int(env, name: str, default: int) -> int:
    raw = _text(env, name)
    if not raw:
        return default
    return int(raw)
