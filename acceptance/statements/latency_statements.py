from statements.failed_reply_statements import QUESTION, MODEL, REPLY_FAILED
from statements.reply_statements import SCRIPT

LATENCY_MS = 50
KEY = "attempt-latency-1"


class LatencyStatements:
    def when_the_reply_does_not_finish_within_the_chat_latency_budget(self) -> None:
        hung = self.chats.hang_tutor(self.token)
        assert hung.status_code == 204
        self.sent = self.chats.send(
            self.token, self.chat_id, QUESTION, MODEL, "professor", KEY
        )
        self.opened = self.chats.get(self.token, self.chat_id)

    def then_the_reply_work_does_not_continue_after_the_budget(self) -> None:
        calls = self.chats.tutor_calls(self.token)
        assert calls.status_code == 200
        assert calls.body["finished"] is False
        assert len(calls.body["calls"]) == 1

    def and_the_clock_is_fixed(self, when: str) -> None:
        scripted = self.chats.script_tutor(self.token, SCRIPT)
        assert scripted.status_code == 204
        offsets = {
            "just before the chat latency budget expires": LATENCY_MS - 1,
            "at the instant the chat latency budget expires": LATENCY_MS,
            "just after the chat latency budget expires": LATENCY_MS + 1,
        }
        advanced = self.chats.advance_on_match(self.token, offsets[when])
        assert advanced.status_code == 204
        self.pin_when = when

    def when_the_person_sends_a_line(self) -> None:
        self.sent = self.chats.send(
            self.token, self.chat_id, QUESTION, MODEL, "professor", KEY
        )
        self.opened = self.chats.get(self.token, self.chat_id)

    def then_the_tutor_line_is_kept(self) -> None:
        assert self.sent.status_code == 200
        assert self.sent.body is not None
        assert self.sent.body["error"] is None
        roles = [line["role"] for line in self.sent.body["lines"]]
        assert roles == ["person", "tutor"]

    def then_the_thread_has_one_person_line_and_no_tutor_line_and_the_reply_work_stops(
        self,
    ) -> None:
        assert self.sent.status_code == 200
        assert self.sent.body is not None
        assert self.sent.body["error"] == REPLY_FAILED
        assert [line["role"] for line in self.sent.body["lines"]] == ["person"]
        calls = self.chats.tutor_calls(self.token)
        assert calls.body["calls"] == []
