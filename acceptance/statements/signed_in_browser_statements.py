import json
import time
from pathlib import Path

from clients.application.chat_client import ChatClient
from clients.application.document_client import DocumentClient
from clients.application.index_probe import IndexProbe
from clients.application.session_client import ScriptedProvider, SessionClient
from statements.chat_screen_statements import (
    EXAMINER_QUESTION,
    MODEL,
    PAGE,
    PERSON_QUESTION,
    SOCRATIC_QUESTION,
    SOURCE_TEXT_VALUE,
    TUTOR_ANSWER,
)
from uuid import uuid4

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
        self.chats = ChatClient(base_url)
        self.probe = probe
        self.lecture = (FIXTURES / "lecture.pdf").read_bytes()
        self.ready_document = None
        self.token = None
        self.chat = None
        self.person_line = PERSON_QUESTION
        self.tutor_line = TUTOR_ANSWER
        self.source_text = SOURCE_TEXT_VALUE
        self.model = MODEL
        self.page = PAGE

    def given_a_signed_in_person_with_no_documents(self) -> None:
        self._open_session("ada@example.test", "Ada")

    def given_a_signed_in_person_with_a_ready_pdf_named_matanaliz(self) -> None:
        token = self._open_session("ada@example.test", "Ada")
        self.token = token
        uploaded = self.documents.submit_pdf(token, READY_NAME, self.lecture)
        assert uploaded.status_code == 201
        self.probe.release_indexing()
        self.ready_document = self._until_ready(token, uploaded.body["id"])
        assert self.ready_document.status_code == 200
        assert self.ready_document.body["status"] == "ready"
        assert self.ready_document.body["name"] == READY_NAME
        self.probe.hold_indexing()

    def given_a_signed_in_person_with_a_selected_ready_pdf(self) -> None:
        self.given_a_signed_in_person_with_a_ready_pdf_named_matanaliz()

    def given_a_signed_in_person_with_a_chat_that_has_a_person_line_and_a_tutor_line(self) -> None:
        self.given_a_signed_in_person_with_a_ready_pdf_named_matanaliz()
        document_id = self.ready_document.body["id"]
        seeded = self.chats.seed_search(
            self.token,
            document_id,
            ({"text": self.source_text, "page": self.page},),
        )
        assert seeded.status_code == 204
        created = self.chats.create(self.token, document_id)
        assert created.status_code == 201
        scripted = self.chats.script_tutor(self.token, self.tutor_line)
        assert scripted.status_code == 204
        sent = self.chats.send(
            self.token,
            created.body["id"],
            self.person_line,
            self.model,
            "professor",
            "ui-seed-1",
        )
        assert sent.status_code == 200
        opened = self.chats.get(self.token, created.body["id"])
        assert opened.status_code == 200
        self.chat = opened.body

    def given_a_signed_in_person_with_an_askable_chat(self) -> None:
        self.given_a_signed_in_person_with_a_ready_pdf_named_matanaliz()
        document_id = self.ready_document.body["id"]
        seeded = self.chats.seed_search(
            self.token,
            document_id,
            ({"text": self.source_text, "page": self.page},),
        )
        assert seeded.status_code == 204
        created = self.chats.create(self.token, document_id)
        assert created.status_code == 201
        scripted = self.chats.script_tutor(self.token, self.tutor_line)
        assert scripted.status_code == 204
        self.chat = created.body
        self.chat_id = created.body["id"]

    def script_tutor(self, text: str) -> None:
        scripted = self.chats.script_tutor(self.token, text)
        assert scripted.status_code == 204

    def given_a_signed_in_person_whose_tutor_is_withholding(self) -> None:
        self.given_a_signed_in_person_with_an_askable_chat()
        self.script_tutor(SOCRATIC_QUESTION)
        sent = self.chats.send(
            self.token,
            self.chat_id,
            self.person_line,
            self.model,
            "socratic",
            str(uuid4()),
        )
        assert sent.status_code == 200
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        self.chat = opened.body

    def given_a_signed_in_person_with_an_open_examiner_question(self) -> None:
        self.given_a_signed_in_person_with_an_askable_chat()
        self.script_tutor(EXAMINER_QUESTION)
        sent = self.chats.send_payload(
            self.token, self.chat_id, {"mode": "examiner"}, str(uuid4())
        )
        assert sent.status_code == 200
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        self.chat = opened.body

    def given_a_signed_in_person_whose_examiner_question_is_already_graded(self) -> None:
        self.given_a_signed_in_person_with_an_open_examiner_question()
        for _ in range(2):
            self.script_tutor(EXAMINER_QUESTION)
            graded = self.chats.send_payload(
                self.token, self.chat_id, {"choice_id": "c1"}, str(uuid4())
            )
            assert graded.status_code == 200
            assert graded.body["lines"][-1]["kind"] == "question"
        wrong = self.chats.send_payload(
            self.token, self.chat_id, {"choice_id": "c2"}, str(uuid4())
        )
        assert wrong.status_code == 200
        assert wrong.body["lines"][0]["kind"] == "grade"
        assert wrong.body["lines"][0]["correct"] is False
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body["lines"][-1]["kind"] == "grade"
        self.chat = opened.body

    def given_a_signed_in_person_whose_examiner_series_has_three_grades(self) -> None:
        self.given_a_signed_in_person_whose_examiner_question_is_already_graded()
        self.examiner_question_texts = [
            line["text"]
            for line in self.chat["lines"]
            if line.get("kind") == "question"
        ]
        assert len(self.examiner_question_texts) == 3
        self.script_tutor(self.tutor_line)

    def given_a_signed_in_person_whose_reply_will_fail(self) -> None:
        self.given_a_signed_in_person_with_an_askable_chat()
        failed = self.chats.fail_tutor(self.token)
        assert failed.status_code == 204
        self.failure_message = "The model could not answer"

    def and_the_tutor_reply_is_held(self) -> None:
        self.script_tutor(self.tutor_line)
        held = self.chats.hold_tutor(self.token)
        assert held.status_code == 204

    def release_held_tutor(self) -> None:
        released = self.chats.release_tutor(self.token)
        assert released.status_code == 204

    def given_a_guest(self) -> None:
        self.driver.get(self.app_url)
        self.driver.execute_script(
            "window.localStorage.removeItem(arguments[0]);",
            STORAGE_KEY,
        )

    def given_the_document_list_cannot_be_read(self) -> None:
        self.probe.set_document_store_down()

    def given_a_signed_in_person_with_a_document_that_failed_on_page_12(self) -> None:
        token = self._open_session("ada@example.test", "Ada")
        self.probe.hold_indexing()
        uploaded = self.documents.submit_pdf(token, "Методичка.pdf", self.lecture)
        assert uploaded.status_code == 201
        self.probe.force_failed_document(
            uploaded.body["id"],
            "Не удалось прочитать страницу 12",
        )
        failed = self.documents.read(token, uploaded.body["id"])
        assert failed.status_code == 200
        assert failed.body["status"] == "failed"
        assert failed.body["error"] == "Не удалось прочитать страницу 12"
    def when_indexing_is_released(self) -> None:
        self.probe.release_indexing()

    def close(self) -> None:
        self.sessions.close()
        self.documents.close()
        self.chats.close()

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
