from application.context import build_production_context
from application.settings import StartupError


class StartupStatements:
    _BASE_ENV = {
        "OAUTH_PROVIDER": "fake",
        "DATABASE_URL": "postgresql+asyncpg://user:password@localhost:5432/adaptive_tutor",
        "REDIS_URL": "redis://localhost:6379/0",
        "JWT_ACCESS_SECRET": "a" * 32,
        "JWT_REFRESH_SECRET": "b" * 32,
        "QDRANT_URL": "http://localhost:6333",
        "CLAMAV_HOST": "127.0.0.1",
        "CLAMAV_PORT": "3310",
    }

    _OMIT = {
        "the document store": ("DATABASE_URL", "DATABASE"),
        "the search store": ("QDRANT_URL", "Qdrant"),
        "the virus check": ("CLAMAV_HOST", "virus"),
    }

    def __init__(self):
        self._env = dict(self._BASE_ENV)
        self._keyword = ""
        self._startup_error: StartupError | None = None

    def given_setting_is_missing(self, setting: str) -> None:
        key, keyword = self._OMIT[setting]
        self._keyword = keyword
        self._env = dict(self._BASE_ENV)
        self._env.pop(key, None)

    def when_the_app_starts(self) -> None:
        self._startup_error = None
        try:
            build_production_context(self._env)
        except StartupError as error:
            self._startup_error = error

    def then_startup_fails_before_it_accepts_an_upload(self) -> None:
        if self._startup_error is None:
            raise AssertionError("startup accepted an upload")
        assert self._keyword.lower() in str(self._startup_error).lower()

    def then_it_does_not_pretend_the_check_passed(self) -> None:
        if self._startup_error is None:
            raise AssertionError("startup accepted an upload")
        message = str(self._startup_error).lower()
        assert message
        assert "unset" in message or "missing" in message or "is unset" in message
