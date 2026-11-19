from statements.reply_statements import MODEL, QUESTION, SCRIPT


class InterleaveSendStatements:
    def when_two_different_attempts_interleave_between_the_read_of_the_thread_and_the_write(
        self,
    ) -> None:
        scripted = self.chats.script_tutor(self.token, SCRIPT)
        assert scripted.status_code == 204
        armed = self.chats.arm_thread_interleave(self.token)
        assert armed.status_code == 204
        self.interleaved = self.chats.interleave_sends(
            self.token,
            self.chat_id,
            [
                {
                    "key": "attempt-a",
                    "text": "first concurrent question",
                    "model": MODEL,
                    "mode": "professor",
                },
                {
                    "key": "attempt-b",
                    "text": "second concurrent question",
                    "model": MODEL,
                    "mode": "professor",
                },
            ],
        )

    def then_both_person_lines_remain_in_the_thread(self) -> None:
        assert self.interleaved.status_code == 200
        assert self.interleaved.body is not None
        assert self.interleaved.body["sends"][0]["error"] is None
        assert self.interleaved.body["sends"][1]["error"] is None
        roles = [line["role"] for line in self.interleaved.body["thread"]["lines"]]
        texts = [line["text"] for line in self.interleaved.body["thread"]["lines"]]
        assert roles.count("person") == 2
        assert roles.count("tutor") == 2
        assert "first concurrent question" in texts
        assert "second concurrent question" in texts

    def and_neither_replaces_the_other(self) -> None:
        lines = self.interleaved.body["thread"]["lines"]
        assert len(lines) == 4
        person_texts = [line["text"] for line in lines if line["role"] == "person"]
        assert person_texts == [
            "first concurrent question",
            "second concurrent question",
        ] or person_texts == [
            "second concurrent question",
            "first concurrent question",
        ]

    def when_two_deliveries_of_the_same_attempt_interleave_between_the_read_of_that_attempt_and_the_write(
        self,
    ) -> None:
        scripted = self.chats.script_tutor(self.token, SCRIPT)
        assert scripted.status_code == 204
        armed = self.chats.arm_attempt_interleave(self.token)
        assert armed.status_code == 204
        self.interleaved = self.chats.interleave_sends(
            self.token,
            self.chat_id,
            [
                {
                    "key": "same-attempt-key",
                    "text": QUESTION,
                    "model": MODEL,
                    "mode": "professor",
                },
                {
                    "key": "same-attempt-key",
                    "text": QUESTION,
                    "model": MODEL,
                    "mode": "professor",
                },
            ],
        )

    def then_the_interleaved_thread_contains_one_person_line_and_one_tutor_line(self) -> None:
        assert self.interleaved.status_code == 200
        assert self.interleaved.body is not None
        roles = [line["role"] for line in self.interleaved.body["thread"]["lines"]]
        assert roles == ["person", "tutor"]
        assert self.interleaved.body["sends"][0]["lines"] == self.interleaved.body["sends"][1]["lines"]
