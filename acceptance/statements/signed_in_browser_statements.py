import json
import time
from pathlib import Path

from clients.application.document_client import DocumentClient
from clients.application.index_probe import IndexProbe
from clients.application.session_client import ScriptedProvider, SessionClient

STORAGE_KEY = "adaptivetutor.session"
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
READY_NAME = "Матанализ.pdf"


class SignedInBrowserStatements:
    def __init__(
        self,
        driver,
        app_url: str,
        base_url: str,
        provider: ScriptedProvider,
        probe: IndexProbe,
    ):
        self.driver = driver
        self.app_url = app_url
        self.sessions = SessionClient(base_url, provider)
        self.documents = DocumentClient(base_url)
        self.probe = probe
        self.lecture = (FIXTURES / "lecture.pdf").read_bytes()
        self.ready_document = None

    def given_a_signed_in_person_with_no_documents(self) -> None:
        self._open_session("ada@example.test", "Ada")

    def given_a_signed_in_person_with_a_ready_pdf_named_matanaliz(self) -> None:
        token = self._open_session("ada@example.test", "Ada")
        uploaded = self.documents.submit_pdf(token, READY_NAME, self.lecture)
        assert uploaded.status_code == 201
        self.probe.release_indexing()
        self.ready_document = self._until_ready(token, uploaded.body["id"])
        assert self.ready_document.status_code == 200
        assert self.ready_document.body["status"] == "ready"
        assert self.ready_document.body["name"] == READY_NAME
        self.probe.hold_indexing()

    def when_indexing_is_released(self) -> None:
        self.probe.release_indexing()

    def close(self) -> None:
        self.sessions.close()
        self.documents.close()

    def _open_session(self, email: str, name: str) -> str:
        opened = self.sessions.open_account(email, name)
        assert opened.status_code == 200
        assert opened.body["token_type"] == "bearer"
        session = {
            "accessToken": opened.body["access_token"],
            "refreshToken": opened.body["refresh_token"],
            "userId": "",
            "displayName": "",
            "avatarUrl": None,
        }
        self.driver.get(self.app_url)
        self.driver.execute_script(
            "window.localStorage.setItem(arguments[0], arguments[1]);",
            STORAGE_KEY,
            json.dumps(session),
        )
        self.driver.get(self.app_url)
        return opened.body["access_token"]

    def _until_ready(self, token: str, document_id: str):
        deadline = time.monotonic() + 30
        seen = None
        while time.monotonic() < deadline:
            seen = self.documents.read(token, document_id)
            if seen.status_code == 200 and seen.body["status"] in {"ready", "failed"}:
                break
            time.sleep(0.05)
        return seen
