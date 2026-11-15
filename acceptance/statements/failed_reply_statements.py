QUESTION = "What does the lecture say about photosynthesis?"
MODEL = "qwen/qwen3-32b"
FAILED_KEY = "attempt-failed-1"
NEW_KEY = "attempt-after-fail"
REPLY_FAILED = {"code": "reply_failed", "message": "The model could not answer"}


class FailedReplyStatements:
    def and_the_reply_fails_after_the_vectors_are_ready(self) -> None:
        failed = self.chats.fail_tutor(self.token)
        assert failed.status_code == 204
        self.failed_key = FAILED_KEY
        self.sent = self.chats.send(
            self.token, self.chat_id, QUESTION, MODEL, "professor", self.failed_key
        )
        assert self.sent.status_code == 200
        assert self.sent.body is not None
        assert self.sent.body["error"] == REPLY_FAILED
        assert len(self.sent.body["lines"]) == 1
        assert self.sent.body["lines"][0]["role"] == "person"

    def when_the_person_repeats_that_same_attempt(self) -> None:
        self.sent = self.chats.send(
            self.token, self.chat_id, QUESTION, MODEL, "professor", self.failed_key
        )
        self.opened = self.chats.get(self.token, self.chat_id)

    def then_the_thread_has_one_person_line(self) -> None:
        assert self.sent is not None and self.sent.body is not None
        assert self.sent.status_code == 200
        assert self.sent.body["error"] == REPLY_FAILED
        assert [line["role"] for line in self.sent.body["lines"]] == ["person"]
        assert self.opened is not None and self.opened.body is not None
        assert self.opened.status_code == 200
        people = [line for line in self.opened.body["lines"] if line["role"] == "person"]
        assert len(people) == 1
        assert people[0]["text"] == QUESTION

    def then_the_thread_has_no_tutor_line(self) -> None:
        assert self.sent is not None and self.sent.body is not None
        assert all(line["role"] != "tutor" for line in self.sent.body["lines"])
        assert self.opened is not None and self.opened.body is not None
        assert all(line["role"] != "tutor" for line in self.opened.body["lines"])

    def given_a_signed_in_person_whose_last_reply_failed(self) -> None:
        self.given_a_signed_in_person_with_an_askable_chat()
        self.and_the_reply_fails_after_the_vectors_are_ready()

    def when_the_person_sends_a_new_attempt(self) -> None:
        self.new_question = "And what about respiration?"
        self.sent = self.chats.send(
            self.token, self.chat_id, self.new_question, MODEL, "professor", NEW_KEY
        )
        self.opened = self.chats.get(self.token, self.chat_id)

    def then_that_person_line_is_kept(self) -> None:
        assert self.sent is not None and self.sent.body is not None
        assert self.sent.status_code == 200
        assert self.sent.body["error"] == REPLY_FAILED
        assert [line["text"] for line in self.sent.body["lines"]] == [self.new_question]
        assert self.opened is not None and self.opened.body is not None
        texts = [line["text"] for line in self.opened.body["lines"] if line["role"] == "person"]
        assert texts == [QUESTION, self.new_question]
