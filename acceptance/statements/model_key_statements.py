from uuid import uuid4

from statements.failed_reply_statements import REPLY_FAILED
from statements.reply_statements import MODEL, QUESTION


class ModelKeyStatements:
    def given_the_app_is_running_with_the_model_key_unset(self) -> None:
        self.given_a_signed_in_person_with_an_askable_chat()
        cleared = self.chats.clear_model_key(self.token)
        assert cleared.status_code == 204

    def when_the_person_sends_a_line_with_no_model_key(self) -> None:
        self.sent = self.chats.send(
            self.token, self.chat_id, QUESTION, MODEL, "professor", str(uuid4())
        )
        self.opened = self.chats.get(self.token, self.chat_id)

    def then_the_reply_fails_without_secret_stack_or_path(self) -> None:
        assert self.sent.status_code == 200
        assert self.sent.body is not None
        assert self.sent.body["error"] == REPLY_FAILED
        blob = str(self.sent.body)
        assert "traceback" not in blob.lower()
        assert "FREE_LLM" not in blob
        assert "\\" not in blob
        assert "/" not in self.sent.body["error"]["message"]
        assert self.opened.status_code == 200
        assert self.opened.body is not None
        roles = [line["role"] for line in self.opened.body["lines"]]
        assert roles == ["person"]
