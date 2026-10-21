1) Ссылки, данные должны браться из .env 
1.1)
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
1.2) 
    access_ttl=timedelta(minutes=_int(env, "ACCESS_TOKEN_EXPIRE_MINUTES", 60)),
        refresh_ttl=timedelta(minutes=_int(env, "REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 30)),
1.3) 
    _CHUNK = 64 * 1024
