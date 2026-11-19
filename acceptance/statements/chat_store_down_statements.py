from uuid import uuid4

from statements.reply_statements import MODEL, QUESTION, SCRIPT

CHAT_STORE_DOWN = {"code": "unavailable", "message": "Chat store is unavailable"}


class ChatStoreDownStatements:
    def given_a_signed_in_person_who_has_a_chat(self) -> None:
        self.given_a_signed_in_person_with_an_askable_chat()
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        self.thread_before_outage = list(opened.body["lines"])

    def and_the_chat_store_is_down(self) -> None:
        failed = self.chats.fail_chat_store(self.token)
        assert failed.status_code == 204

    def when_the_person_reads_the_chat_list_while_store_down(self) -> None:
        self.listed = self.chats.list(self.token)

    def then_the_list_read_is_refused_and_no_chat_is_returned(self) -> None:
        assert self.listed.status_code == 503
        assert self.listed.body == CHAT_STORE_DOWN

    def when_the_person_sends_a_line_while_store_down(self) -> None:
        self.sent = self.chats.send(
            self.token, self.chat_id, QUESTION, MODEL, "professor", str(uuid4())
        )

    def then_the_send_is_refused_and_no_line_is_stored(self) -> None:
        assert self.sent.status_code == 503
        assert self.sent.body == CHAT_STORE_DOWN
        recovered = self.chats.recover_chat_store()
        assert recovered.status_code == 204
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        assert opened.body["lines"] == self.thread_before_outage

    def given_the_chat_store_was_down_and_is_back(self) -> None:
        self.given_a_signed_in_person_who_has_a_chat()
        self.and_the_chat_store_is_down()
        listed = self.chats.list(self.token)
        assert listed.status_code == 503
        recovered = self.chats.recover_chat_store()
        assert recovered.status_code == 204

    def when_the_person_reads_the_chat_after_recovery(self) -> None:
        self.opened = self.chats.get(self.token, self.chat_id)

    def then_the_thread_is_the_thread_from_before_the_outage(self) -> None:
        assert self.opened.status_code == 200
        assert self.opened.body is not None
        assert self.opened.body["lines"] == self.thread_before_outage

    def when_the_person_sends_a_line_after_recovery(self) -> None:
        scripted = self.chats.script_tutor(self.token, SCRIPT)
        assert scripted.status_code == 204
        self.sent = self.chats.send(
            self.token, self.chat_id, QUESTION, MODEL, "professor", str(uuid4())
        )

    def then_that_line_is_stored_once(self) -> None:
        assert self.sent.status_code == 200
        assert self.sent.body is not None
        assert len(self.sent.body["lines"]) == 2
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        people = [line for line in opened.body["lines"] if line["role"] == "person"]
        assert len(people) == 1
        assert people[0]["text"] == QUESTION

    def when_the_person_reads_a_chat_while_store_down(self) -> None:
        self.call = self.chats.get(self.token, self.chat_id)

    def when_the_person_starts_a_chat_while_store_down(self) -> None:
        self.call = self.chats.create(self.token, self.document_id)

    def when_the_person_opens_a_chat_for_a_document_while_store_down(self) -> None:
        self.call = self.chats.open(self.token, self.document_id)

    def then_the_call_is_refused_and_no_chat_is_created(self) -> None:
        assert self.call.status_code == 503
        assert self.call.body == CHAT_STORE_DOWN
        recovered = self.chats.recover_chat_store()
        assert recovered.status_code == 204
        listed = self.chats.list(self.token)
        assert listed.status_code == 200
        assert listed.body is not None
        assert len(listed.body["chats"]) == 1
