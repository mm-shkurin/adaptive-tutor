from clients.application.quiz_client import QuizClient
from statements.signed_in_browser_statements import READY_NAME, SECOND_NAME

SCRIPT_MARK = "<script>alert(1)</script>"


def valid_quiz_body(count: int = 5, page: int = 2) -> dict:
    return {
        "questions": [
            {
                "text": f"Question {index}",
                "choices": [f"q{index}c{choice}" for choice in range(4)],
                "correct_index": 0,
                "page": page,
            }
            for index in range(count)
        ]
    }


def scripted_xss_body(count: int = 3, page: int = 2) -> dict:
    return {
        "questions": [
            {
                "text": f"Question {index} {SCRIPT_MARK}" if index == 0 else f"Question {index}",
                "choices": [
                    f"A {SCRIPT_MARK}" if index == 0 else f"q{index}c0",
                    f"q{index}c1",
                    f"q{index}c2",
                    f"q{index}c3",
                ],
                "correct_index": 0,
                "page": page,
            }
            for index in range(count)
        ]
    }


class QuizBrowserStatements:
    def __init__(self, signed_in):
        self.signed_in = signed_in
        self.quizzes = QuizClient(str(signed_in.sessions.http.base_url))
        self.quiz = None
        self.quiz_id = None
        self.ready_names = []
        self.not_ready_names = []
        self.script_mark = SCRIPT_MARK

    def given_a_signed_in_person_with_no_quiz(self) -> None:
        token = self.signed_in._open_session("ada@example.test", "Ada")
        self.signed_in.token = token
        listed = self.quizzes.list(token)
        assert listed.status_code == 200, listed.body
        assert listed.body == {"quizzes": []}

    def given_a_signed_in_person_with_two_ready_pdfs(self) -> None:
        self.signed_in.given_a_signed_in_person_with_a_ready_pdf_named_matanaliz()
        uploaded = self.signed_in.documents.submit_pdf(
            self.signed_in.token, SECOND_NAME, self.signed_in.lecture
        )
        assert uploaded.status_code == 201
        self.signed_in.probe.release_indexing()
        second = self.signed_in._until_ready(self.signed_in.token, uploaded.body["id"])
        assert second.status_code == 200
        assert second.body["status"] == "ready"
        self.signed_in.probe.hold_indexing()
        self.ready_names = [READY_NAME, SECOND_NAME]
        self._seed(self.signed_in.ready_document.body["id"])
        self._seed(second.body["id"])

    def given_a_signed_in_person_with_ready_and_not_ready_pdfs(self) -> None:
        self.signed_in.given_a_signed_in_person_with_a_ready_pdf_named_matanaliz()
        self.ready_names = [READY_NAME]
        self.not_ready_names = []
        self._seed(self.signed_in.ready_document.body["id"])
        for state in ("waiting", "indexing", "failed"):
            name = f"{state}.pdf"
            uploaded = self.signed_in.documents.submit_pdf(
                self.signed_in.token, name, self.signed_in.lecture
            )
            assert uploaded.status_code == 201
            document_id = uploaded.body["id"]
            if state == "waiting":
                seen = self.signed_in.documents.read(self.signed_in.token, document_id)
                assert seen.status_code == 200
                assert seen.body["status"] == "waiting"
            elif state == "indexing":
                moved = self.signed_in.documents.move_indexing_status(
                    self.signed_in.token, document_id, "indexing"
                )
                assert moved.status_code == 200
                assert moved.body["status"] == "indexing"
            else:
                indexing = self.signed_in.documents.move_indexing_status(
                    self.signed_in.token, document_id, "indexing"
                )
                assert indexing.status_code == 200
                failed = self.signed_in.documents.move_indexing_status(
                    self.signed_in.token, document_id, "failed", "broken"
                )
                assert failed.status_code == 200
                assert failed.body["status"] == "failed"
            self.not_ready_names.append(name)

    def given_a_signed_in_person_on_an_unanswered_question(self) -> None:
        self._open_quiz(count=3)
        opened = self.quizzes.get(self.signed_in.token, self.quiz_id)
        assert opened.status_code == 200
        assert opened.body["status"] == "take"
        assert opened.body["current_index"] == 0

    def given_a_signed_in_person_with_a_finished_quiz(self) -> None:
        self._open_quiz(count=3)
        self._finish("right")

    def given_a_signed_in_person_with_a_finished_quiz_started_again(self) -> None:
        self.given_a_signed_in_person_with_a_finished_quiz()
        again = self.quizzes.retry(self.signed_in.token, self.quiz_id)
        assert again.status_code == 200
        assert again.body["status"] == "take"
        self.quiz = again.body

    def given_a_signed_in_person_with_a_script_marked_quiz(self) -> None:
        self.signed_in.given_a_signed_in_person_with_a_ready_pdf_named_matanaliz()
        document_id = self.signed_in.ready_document.body["id"]
        self._seed(document_id)
        scripted = self.quizzes.script_tutor(
            self.signed_in.token, scripted_xss_body(count=3)
        )
        assert scripted.status_code == 204
        topic = f"Topic {SCRIPT_MARK}"
        created = self.quizzes.create(self.signed_in.token, document_id, topic, 3)
        assert created.status_code == 201
        self.quiz = created.body
        self.quiz_id = created.body["id"]

    def given_a_signed_in_person_mid_quiz_after_one_answer(self) -> None:
        self._open_quiz(count=3)
        choice = self.quiz["questions"][0]["choices"][0]["id"]
        answered = self.quizzes.answer(self.signed_in.token, self.quiz_id, choice)
        assert answered.status_code == 200
        advanced = self.quizzes.advance(self.signed_in.token, self.quiz_id)
        assert advanced.status_code == 200
        self.quiz = advanced.body

    def and_the_quiz_tutor_is_held(self) -> None:
        held = self.quizzes.hold_tutor(self.signed_in.token)
        assert held.status_code == 204

    def and_the_quiz_tutor_will_fail(self) -> None:
        failed = self.quizzes.fail_tutor(self.signed_in.token)
        assert failed.status_code == 204

    def release_held_quiz_tutor(self) -> None:
        released = self.quizzes.release_tutor(self.signed_in.token)
        assert released.status_code == 204

    def wait_until_quiz_tutor_hold_entered(self) -> None:
        import time

        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            seen = self.quizzes.tutor_holds(self.signed_in.token)
            if seen.status_code == 200 and seen.body.get("entered", 0) >= 1:
                return
            time.sleep(0.05)
        raise AssertionError("quiz tutor hold not entered")

    def then_one_quiz_is_stored(self) -> None:
        listed = self.quizzes.list(self.signed_in.token)
        assert listed.status_code == 200
        assert len(listed.body["quizzes"]) == 1

    def _open_quiz(self, count: int = 5) -> None:
        self.signed_in.given_a_signed_in_person_with_a_ready_pdf_named_matanaliz()
        document_id = self.signed_in.ready_document.body["id"]
        self._seed(document_id)
        scripted = self.quizzes.script_tutor(self.signed_in.token, valid_quiz_body(count))
        assert scripted.status_code == 204
        created = self.quizzes.create(self.signed_in.token, document_id, "cells", count)
        assert created.status_code == 201
        self.quiz = created.body
        self.quiz_id = created.body["id"]

    def _finish(self, how: str) -> None:
        detail = self.quizzes.get(self.signed_in.token, self.quiz_id).body
        while detail["status"] == "take":
            pick = 0 if how == "right" else 1
            chosen = detail["questions"][detail["current_index"]]["choices"][pick]["id"]
            assert self.quizzes.answer(self.signed_in.token, self.quiz_id, chosen).status_code == 200
            advanced = self.quizzes.advance(self.signed_in.token, self.quiz_id)
            assert advanced.status_code == 200
            detail = advanced.body
        self.quiz = detail

    def _seed(self, document_id: str) -> None:
        seeded = self.quizzes.seed_pieces(
            self.signed_in.token,
            document_id,
            [{"page": 2, "text": "alpha"}, {"page": 4, "text": "beta"}],
        )
        assert seeded.status_code == 204
