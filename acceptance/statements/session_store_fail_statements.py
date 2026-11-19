from uuid import uuid4

from statements.chat_gate_statements import MISSING_CHAT
from statements.reply_statements import MODEL, QUESTION


class SessionStoreFailStatements:
    def given_a_signed_in_persons_session_store_fails(self) -> None:
        self.given_a_signed_in_person()
        self.document_id = self._ready_pdf("session-fail.pdf")
        created = self.chats.create(self.token, self.document_id)
        assert created.status_code == 201
        assert created.body is not None
        self.chat_id = created.body["id"]
        self.listed_before = self.chats.list(self.token)
        assert self.listed_before.status_code == 200
        assert self.listed_before.body is not None
        self.lines_before = []
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        self.lines_before = list(opened.body["lines"])
        failed = self.chats.fail_session_store(self.token)
        assert failed.status_code == 204
        self.guest_call = None

    def when_the_person_reads_the_chat_list_with_failed_session_store(self) -> None:
        self.guest_call = self.chats.list(self.token)

    def when_the_person_reads_a_chat_with_failed_session_store(self) -> None:
        self.guest_call = self.chats.get(self.token, self.chat_id)

    def when_the_person_starts_a_chat_with_failed_session_store(self) -> None:
        self.guest_call = self.chats.create(self.token, self.document_id)

    def when_the_person_opens_a_chat_for_a_document_with_failed_session_store(self) -> None:
        self.guest_call = self.chats.open(self.token, self.document_id)

    def when_the_person_sends_a_line_with_failed_session_store(self) -> None:
        self.guest_call = self.chats.send(
            self.token, self.chat_id, QUESTION, MODEL, "professor", str(uuid4())
        )

    def then_the_refusal_matches_a_missing_chat_for_session_store_failure(self) -> None:
        assert self.guest_call is not None
        assert self.guest_call.status_code == 404
        assert self.guest_call.body == MISSING_CHAT

    def then_nothing_is_stored_after_session_store_failure(self) -> None:
        recovered = self.chats.recover_session_store()
        assert recovered.status_code == 204
        listed = self.chats.list(self.token)
        assert listed.status_code == 200
        assert listed.body == self.listed_before.body
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        assert opened.body["lines"] == self.lines_before
