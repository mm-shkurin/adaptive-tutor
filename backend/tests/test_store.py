"""A dead account store refuses the profile, and the process will not boot without Yandex."""

from application.context import build_production_context
from application.settings import StartupError
from tests.support import bearer, build, sign_in


def test_a_dead_account_store_refuses_the_profile_and_then_recovers():
    bundle = build()
    token = sign_in(bundle).json()["access_token"]
    before = bundle.client.get("/api/v1/user/profile", headers=bearer(token)).json()
    bundle.store.dead = True
    refused = bundle.client.get("/api/v1/user/profile", headers=bearer(token))
    rename = bundle.client.patch("/api/v1/user/profile", headers=bearer(token), json={"name": "Другое"})
    assert refused.status_code == 503
    assert rename.status_code == 503
    assert "name" not in refused.json()
    assert refused.json()["code"] == "unavailable"
    assert bundle.store.live == 0
    for _ in range(20):
        assert bundle.client.get("/api/v1/user/profile", headers=bearer(token)).status_code == 503
    assert bundle.store.live == 0
    bundle.store.dead = False
    restored = bundle.client.get("/api/v1/user/profile", headers=bearer(token))
    assert restored.status_code == 200
    assert restored.json()["name"] == before["name"]
    assert restored.json()["email"] == before["email"]
    assert restored.json()["created_at"] == before["created_at"]


def test_the_app_refuses_to_start_when_yandex_settings_are_missing():
    env = {
        "OAUTH_PROVIDER": "yandex",
        "DATABASE_URL": "postgresql+asyncpg://user:password@localhost:5432/adaptive_tutor",
        "REDIS_URL": "redis://localhost:6379/0",
        "JWT_ACCESS_SECRET": "a" * 32,
        "JWT_REFRESH_SECRET": "b" * 32,
    }
    try:
        build_production_context(env)
    except StartupError as error:
        assert "Yandex" in str(error)
    else:
        raise AssertionError("startup accepted a guest")
    guest = build().client.post("/api/v1/auth/guest/login", json={"device_id": "phone"})
    assert guest.status_code == 404
