from application.settings import load_settings


def test_missing_model_key_does_not_stop_startup():
    env = {
        "DATABASE_URL": "postgresql+asyncpg://u:p@localhost/db",
        "REDIS_URL": "redis://localhost:6379/0",
        "JWT_ACCESS_SECRET": "a" * 32,
        "JWT_REFRESH_SECRET": "b" * 32,
        "OAUTH_PROVIDER": "fake",
        "QDRANT_URL": "http://localhost:6333",
        "CLAMAV_HOST": "localhost",
    }
    settings = load_settings(env)
    assert settings.free_llm_api_key == ""
