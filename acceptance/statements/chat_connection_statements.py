from uuid import uuid4

from statements.reply_statements import MODEL, QUESTION, SCRIPT

CHAT_STORE_DOWN = {"code": "unavailable", "message": "Chat store is unavailable"}
REPLY_FAILED = {"code": "reply_failed", "message": "The model could not answer"}


class ChatConnectionStatements:
    def given_the_chat_store_connection_baselines(self) -> None:
        counted = self.chats.store_connections(self.token)
        assert counted.status_code == 200
        assert counted.body is not None
        self.baseline_chat_store = counted.body["chat_store"]
        self.baseline_search_store = counted.body["search_store"]

    def when_several_sends_fail_because_the_chat_store_or_the_search_store_is_unavailable(
        self,
    ) -> None:
        failed = self.chats.fail_chat_store(self.token)
        assert failed.status_code == 204
        for _ in range(3):
            refused = self.chats.send(
                self.token, self.chat_id, QUESTION, MODEL, "professor", str(uuid4())
            )
            assert refused.status_code == 503
            assert refused.body == CHAT_STORE_DOWN
        recovered = self.chats.recover_chat_store()
        assert recovered.status_code == 204
        armed = self.chats.fail_search(self.token)
        assert armed.status_code == 204
        for _ in range(3):
            failed_reply = self.chats.send(
                self.token, self.chat_id, QUESTION, MODEL, "professor", str(uuid4())
            )
            assert failed_reply.status_code == 200
            assert failed_reply.body is not None
            assert failed_reply.body["error"] == REPLY_FAILED
        cleared = self.chats.recover_search()
        assert cleared.status_code == 204

    def then_the_open_store_connections_return_to_the_baseline(self) -> None:
        counted = self.chats.store_connections(self.token)
        assert counted.status_code == 200
        assert counted.body is not None
        assert counted.body["chat_store"] == self.baseline_chat_store
        assert counted.body["search_store"] == self.baseline_search_store

    def then_a_further_send_can_still_be_stored_once_the_store_is_back(self) -> None:
        scripted = self.chats.script_tutor(self.token, SCRIPT)
        assert scripted.status_code == 204
        sent = self.chats.send(
            self.token, self.chat_id, QUESTION, MODEL, "professor", str(uuid4())
        )
        assert sent.status_code == 200
        assert sent.body is not None
        assert sent.body["error"] is None
        people = [line for line in sent.body["lines"] if line["role"] == "person"]
        tutors = [line for line in sent.body["lines"] if line["role"] == "tutor"]
        assert len(people) == 1
        assert people[0]["text"] == QUESTION
        assert len(tutors) == 1
        assert tutors[0]["text"] == SCRIPT
