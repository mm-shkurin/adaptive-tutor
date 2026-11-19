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
    RELEASE,
    SOCRATIC_QUESTION,
    SOURCE_TEXT_VALUE,
    TUTOR_ANSWER,
)
from uuid import uuid4

STORAGE_KEY = "adaptivetutor.session"
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
READY_NAME = "Матанализ.pdf"
SECOND_NAME = "Алгебра.pdf"
EARLIER_ANSWER = "Earlier tutor reply for the first send."
LATER_ANSWER = "Later tutor reply for the second send."
EARLIER_QUESTION = "Первый вопрос пока в полёте"
LATER_QUESTION = "Второй вопрос обгоняет первый"


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
        stretched = self.chats.set_chat_latency(self.token, 30_000)
        assert stretched.status_code == 204
        held = self.chats.hold_tutor(self.token)
        assert held.status_code == 204

    def release_held_tutor(self) -> None:
        released = self.chats.release_tutor(self.token)
        assert released.status_code == 204

    def _stretch_chat_latency_for_holds(self) -> None:
        stretched = self.chats.set_chat_latency(self.token, 30_000)
        assert stretched.status_code == 204

    def given_a_signed_in_person_with_two_ready_pdfs_and_an_askable_chat(self) -> None:
        self.given_a_signed_in_person_with_an_askable_chat()
        uploaded = self.documents.submit_pdf(self.token, SECOND_NAME, self.lecture)
        assert uploaded.status_code == 201
        self.probe.release_indexing()
        second = self._until_ready(self.token, uploaded.body["id"])
        assert second.status_code == 200
        assert second.body["status"] == "ready"
        self.probe.hold_indexing()
        seeded = self.chats.seed_search(
            self.token,
            second.body["id"],
            ({"text": "Алгебраическая структура с операцией.", "page": 2},),
        )
        assert seeded.status_code == 204
        self.second_document = second.body
        self.first_document = self.ready_document.body
        self.left_chat_id = self.chat_id

    def given_a_signed_in_person_whose_last_reply_is_not_in_the_material(self) -> None:
        self.given_a_signed_in_person_with_an_askable_chat()
        document_id = self.ready_document.body["id"]
        seeded = self.chats.seed_search(self.token, document_id, ())
        assert seeded.status_code == 204
        sent = self.chats.send(
            self.token,
            self.chat_id,
            self.person_line,
            self.model,
            "professor",
            str(uuid4()),
        )
        assert sent.status_code == 200
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        self.chat = opened.body

    def then_one_person_and_one_tutor_line_are_stored(self) -> None:
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        roles = [line["role"] for line in opened.body["lines"]]
        assert roles.count("person") == 1
        assert roles.count("tutor") == 1

    def document_count(self) -> int:
        listed = self.documents.list_documents(self.token)
        assert listed.status_code == 200
        return len(listed.body.get("documents") or [])

    def then_no_document_was_added(self, before: int) -> None:
        assert self.document_count() == before

    def then_the_left_chat_stored_the_tutor_reply(self) -> None:
        deadline = time.time() + 20
        while time.time() < deadline:
            opened = self.chats.get(self.token, self.left_chat_id)
            assert opened.status_code == 200
            texts = [line.get("text") for line in opened.body["lines"]]
            if self.tutor_line in texts:
                return
            time.sleep(0.05)
        raise AssertionError("left chat never stored the tutor reply")

    def and_two_ordered_tutor_replies_are_held(self) -> None:
        self._stretch_chat_latency_for_holds()
        held = self.chats.hold_each_tutor(
            self.token, [EARLIER_ANSWER, LATER_ANSWER]
        )
        assert held.status_code == 204
        self.earlier_answer = EARLIER_ANSWER
        self.later_answer = LATER_ANSWER
        self.earlier_question = EARLIER_QUESTION
        self.later_question = LATER_QUESTION

    def wait_until_tutor_holds_entered(self, count: int) -> None:
        deadline = time.time() + 20
        while time.time() < deadline:
            seen = self.chats.tutor_holds(self.token)
            assert seen.status_code == 200
            if seen.body is not None and seen.body.get("entered", 0) >= count:
                return
            time.sleep(0.05)
        raise AssertionError(f"tutor holds entered < {count}")

    def release_tutor_call(self, index: int) -> None:
        released = self.chats.release_tutor_call(self.token, index)
        assert released.status_code == 204

    def then_one_examiner_question_is_stored(self) -> None:
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        questions = [line for line in opened.body["lines"] if line.get("kind") == "question"]
        assert len(questions) == 1

    def then_one_grade_effect_is_stored(self) -> None:
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        grades = [line for line in opened.body["lines"] if line.get("kind") == "grade"]
        assert len(grades) == 1

    def then_one_tell_release_is_stored(self) -> None:
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        releases = [
            line
            for line in opened.body["lines"]
            if line.get("role") == "tutor" and line.get("kind") == "reply"
        ]
        assert len(releases) == 1
        assert releases[0]["text"] == RELEASE

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
