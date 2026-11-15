from uuid import uuid4

from statements.reply_statements import MODEL, QUESTION


class ChatGateStatements:
    def given_a_signed_in_person_with_no_ready_pdf(self) -> None:
        self.given_a_signed_in_person()
        waiting = self.documents.submit_pdf(self.token, "waiting.pdf", self.lecture)
        assert waiting.status_code == 201

    def when_the_person_starts_a_chat(self) -> None:
        self.created = self.chats.create_without_document(self.token)

    def then_the_start_is_refused(self) -> None:
        created = self._created()
        assert created.status_code == 400
        assert created.body == {
            "code": "no_ready_document",
            "message": "No ready document",
        }

    def then_the_chat_list_is_empty(self) -> None:
        listed = self.chats.list(self.token)
        assert listed.status_code == 200
        assert listed.body == {"chats": []}

    def given_a_signed_in_person_with_two_ready_pdfs_and_nothing_selected(self) -> None:
        self.given_a_signed_in_person()
        self.older_id = self._ready_pdf("older-gate.pdf")
        self.clock.advance(60)
        self.newer_id = self._ready_pdf("newer-gate.pdf")

    def and_a_neighbour_who_owns_a_newer_ready_pdf(self) -> None:
        self.clock.advance(60)
        opened = self.sessions.open_account("neil-gate@example.test", "Neil")
        assert opened.status_code == 200
        assert opened.body is not None
        self.neighbour_document_id = self._ready_pdf(
            "neighbour-gate.pdf", opened.body["access_token"]
        )

    def then_the_chat_is_bound_to_the_persons_newer_pdf(self) -> None:
        created = self._created()
        assert created.status_code == 201
        assert created.body is not None
        assert created.body["document_id"] == self.newer_id
        assert created.body["document_id"] != self.older_id

    def then_the_neighbours_pdf_is_not_bound(self) -> None:
        created = self._created()
        assert created.body is not None
        assert created.body["document_id"] != self.neighbour_document_id

    def when_the_person_sends_an_empty_line(self) -> None:
        self.sent = self.chats.send(
            self.token, self.chat_id, "", MODEL, "professor", str(uuid4())
        )

    def when_the_person_sends_a_line_of_only_spaces(self) -> None:
        self.sent = self.chats.send(
            self.token, self.chat_id, "   ", MODEL, "professor", str(uuid4())
        )

    def then_the_send_is_refused_as_empty(self) -> None:
        sent = self._sent()
        assert sent.status_code == 400
        assert sent.body == {"code": "empty_message", "message": "Message is empty"}

    def then_the_thread_is_unchanged_after_refused_send(self) -> None:
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        assert opened.body["lines"] == []

    def _sent(self):
        assert self.sent is not None
        return self.sent
