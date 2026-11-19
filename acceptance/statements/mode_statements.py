from uuid import uuid4

from statements.reply_statements import MODEL, QUESTION, SCRIPT

SOCRATIC_QUESTION = "What would you say photosynthesis needs?"
TELL_UNAVAILABLE = {"code": "tell_unavailable", "message": "Nothing is withheld"}
RELEASE = "Photosynthesis needs light, water, and carbon dioxide."


class ModeStatements:
    def when_the_person_sends_a_question_in_socratic_mode(self) -> None:
        scripted = self.chats.script_tutor(self.token, SOCRATIC_QUESTION)
        assert scripted.status_code == 204
        self.sent = self.chats.send(
            self.token, self.chat_id, QUESTION, MODEL, "socratic", str(uuid4())
        )

    def then_the_tutor_stores_a_question_without_page_or_sources(self) -> None:
        sent = self._sent()
        assert sent.status_code == 200
        assert sent.body is not None
        tutor = sent.body["lines"][1]
        assert tutor == {
            "id": tutor["id"],
            "role": "tutor",
            "text": SOCRATIC_QUESTION,
            "model": None,
            "mode": "socratic",
            "kind": "withheld",
            "page": None,
            "sources": [],
        }
        assert sent.body["lines"][0]["role"] == "person"
        assert sent.body["lines"][0]["text"] == QUESTION

    def given_a_signed_in_person_with_an_askable_chat_that_is_not_withholding(self) -> None:
        self.given_a_signed_in_person_with_an_askable_chat()

    def when_the_person_asks_to_be_told(self) -> None:
        self.sent = self.chats.send_payload(
            self.token, self.chat_id, {"tell": True}, str(uuid4())
        )

    def then_the_tell_is_refused(self) -> None:
        sent = self._sent()
        assert sent.status_code == 400
        assert sent.body == TELL_UNAVAILABLE

    def then_the_thread_is_unchanged_after_tell_refusal(self) -> None:
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        assert opened.body["lines"] == []

    def given_a_signed_in_person_whose_tutor_is_withholding(self) -> None:
        self.given_a_signed_in_person_with_an_askable_chat()
        self.when_the_person_sends_a_question_in_socratic_mode()
        assert self._sent().status_code == 200
        self.withheld_before = self.chats.get(self.token, self.chat_id)
        assert self.withheld_before.status_code == 200

    def when_the_person_sends_a_non_empty_try(self) -> None:
        scripted = self.chats.script_tutor(self.token, RELEASE)
        assert scripted.status_code == 204
        self.try_text = "I think it needs sunlight."
        self.sent = self.chats.send(
            self.token, self.chat_id, self.try_text, MODEL, "professor", str(uuid4())
        )

    def when_the_person_sends_a_non_empty_line_that_asks_to_be_told(self) -> None:
        scripted = self.chats.script_tutor(self.token, RELEASE)
        assert scripted.status_code == 204
        self.try_text = "Please tell me the answer now."
        self.sent = self.chats.send(
            self.token, self.chat_id, self.try_text, MODEL, "professor", str(uuid4())
        )

    def then_that_line_is_kept_as_the_try_and_the_tutor_answers_with_a_page(self) -> None:
        sent = self._sent()
        assert sent.status_code == 200
        assert sent.body is not None
        assert sent.body["lines"][0]["role"] == "person"
        assert sent.body["lines"][0]["text"] == self.try_text
        tutor = sent.body["lines"][1]
        assert tutor["kind"] == "reply"
        assert tutor["text"] == RELEASE
        assert tutor["page"] == self.pieces[0]["page"]
        assert tutor["sources"]
        assert tutor["mode"] == "socratic"

    def when_the_person_uses_the_tell_control(self) -> None:
        scripted = self.chats.script_tutor(self.token, RELEASE)
        assert scripted.status_code == 204
        self.sent = self.chats.send_payload(
            self.token, self.chat_id, {"tell": True}, str(uuid4())
        )

    def then_the_tutor_answers_with_a_page_and_no_person_line_is_added(self) -> None:
        sent = self._sent()
        assert sent.status_code == 200
        assert sent.body is not None
        assert len(sent.body["lines"]) == 1
        tutor = sent.body["lines"][0]
        assert tutor["role"] == "tutor"
        assert tutor["kind"] == "reply"
        assert tutor["text"] == RELEASE
        assert tutor["page"] == self.pieces[0]["page"]
        assert tutor["mode"] == "socratic"
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        roles = [line["role"] for line in opened.body["lines"]]
        assert roles == ["person", "tutor", "tutor"]
        assert opened.body["lines"][1]["kind"] == "withheld"
        assert opened.body["lines"][2]["kind"] == "reply"
