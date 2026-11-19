import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "acceptance"))

import pytest

pytest.register_assert_rewrite(
    "statements.document_statements",
    "statements.chat_statements",
    "statements.reply_statements",
    "statements.failed_reply_statements",
    "statements.vector_open_statements",
    "statements.vector_reuse_statements",
    "statements.partial_vector_statements",
    "statements.latency_statements",
    "statements.interleave_vector_statements",
    "statements.empty_vector_statements",
    "statements.switch_chat_statements",
    "statements.chat_security_statements",
    "statements.list_order_statements",
)

from statements.chat_statements import ChatStatements
from statements.document_statements import DocumentStatements
from statements.startup_statements import StartupStatements
from support.acceptance_server import AcceptanceServer


@pytest.fixture
def startup():
    yield StartupStatements()


@pytest.fixture
def chats():
    server = AcceptanceServer()
    server.start()
    statements = ChatStatements(
        server.base_url, server.provider, server.clock, server.probe, server.fakes
    )
    try:
        yield statements
    finally:
        statements.close()
        server.stop()


@pytest.fixture
def documents():
    server = AcceptanceServer()
    server.start()
    try:
        yield DocumentStatements(
            server.base_url,
            server.provider,
            server.probe,
            server.clock,
            server.rates,
            server.logs,
            server.peak_chat_hold,
        )
    finally:
        server.stop()
