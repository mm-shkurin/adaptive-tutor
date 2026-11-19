from statements.mode_statements import RELEASE
from statements.reply_statements import MODEL


class ModeInterleaveStatements:
    def when_a_try_and_the_tell_control_interleave_between_the_read_of_the_withhold_and_the_write(
        self,
    ) -> None:
        scripted = self.chats.script_tutor(self.token, RELEASE)
        assert scripted.status_code == 204
        armed = self.chats.arm_thread_interleave(self.token)
        assert armed.status_code == 204
        self.interleaved = self.chats.interleave_sends(
            self.token,
            self.chat_id,
            [
                {
                    "key": "try-release",
                    "payload": {
                        "text": "I think it needs sunlight.",
                        "model": MODEL,
                        "mode": "professor",
                    },
                },
                {"key": "tell-release", "payload": {"tell": True}},
            ],
        )

    def then_the_tutor_answers_with_a_page_once_and_the_thread_has_one_release(self) -> None:
        assert self.interleaved.status_code == 200
        assert self.interleaved.body is not None
        thread = self.interleaved.body["thread"]["lines"]
        releases = [
            line
            for line in thread
            if line.get("kind") == "reply" and line.get("mode") == "socratic"
        ]
        assert len(releases) == 1
        assert releases[0]["text"] == RELEASE
        assert releases[0]["page"] == self.pieces[0]["page"]
        withheld = [line for line in thread if line.get("kind") == "withheld"]
        assert len(withheld) == 1

    def given_two_stale_copies_of_that_withhold(self) -> None:
        assert self.chats.get(self.token, self.chat_id).status_code == 200

    def when_one_copy_is_released_by_a_try_and_the_other_by_the_tell_control(self) -> None:
        self.when_a_try_and_the_tell_control_interleave_between_the_read_of_the_withhold_and_the_write()

    def then_one_release_is_kept_and_the_second_save_does_not_drop_it(self) -> None:
        self.then_the_tutor_answers_with_a_page_once_and_the_thread_has_one_release()
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        releases = [
            line
            for line in opened.body["lines"]
            if line.get("kind") == "reply" and line.get("mode") == "socratic"
        ]
        assert len(releases) == 1
        assert releases[0]["text"] == RELEASE
