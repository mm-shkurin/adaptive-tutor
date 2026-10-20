import socket
import threading
import time
from datetime import datetime, timedelta, timezone

import httpx
import uvicorn

from adapters.memory.account_store import MemoryAccountStore
from adapters.memory.oauth_store import MemoryOAuthStore
from adapters.memory.revocations import MemoryRevocations
from adapters.tokens.jwt_tokens import JwtTokens
from application.context import AppContext, RuntimeConfig
from application.main import create_app
from clients.application.index_probe import IndexProbe
from clients.application.session_client import ScriptedProvider
from usecase.account.profile import ProfileService
from usecase.account.session import SessionService
from usecase.account.sign_in import SignIn


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class _Clock:
    def __init__(self):
        self.moment = datetime(2024, 5, 6, 7, 8, 9, tzinfo=timezone.utc)

    def now(self):
        return self.moment


class AcceptanceServer:
    def __init__(self):
        self.provider = ScriptedProvider()
        self.probe = IndexProbe()
        port = _free_port()
        self.base_url = f"http://127.0.0.1:{port}"
        store = MemoryAccountStore()
        clock = _Clock()
        tokens = JwtTokens("a" * 32, "b" * 32, timedelta(minutes=60), timedelta(days=30))
        context = AppContext(
            RuntimeConfig(timedelta(seconds=600), ("http://localhost:5173",)),
            SignIn(
                self.provider,
                MemoryOAuthStore(),
                store,
                tokens,
                clock,
                timedelta(seconds=600),
                timedelta(seconds=120),
                "http://localhost:5173/auth/callback",
            ),
            SessionService(store, tokens, MemoryRevocations()),
            ProfileService(store, self.base_url),
            store,
        )
        app = create_app(context)
        app.state.index_probe = self.probe
        self._server = uvicorn.Server(
            uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning", access_log=False)
        )
        self._thread = threading.Thread(target=self._server.run, daemon=True)

    def start(self) -> None:
        self._thread.start()
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try:
                response = httpx.get(self.base_url + "/health", timeout=0.5)
                if response.status_code == 200:
                    return
            except httpx.HTTPError:
                time.sleep(0.05)
        raise RuntimeError("acceptance backend did not become ready")

    def stop(self) -> None:
        self._server.should_exit = True
        self._thread.join(timeout=5)
