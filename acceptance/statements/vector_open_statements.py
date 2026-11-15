from statements.reply_statements import LECTURE


class VectorOpenStatements:
    def and_a_ready_pdf_with_no_vectors(self) -> None:
        uploaded = self.documents.submit_pdf(self.token, LECTURE, self.lecture)
        assert uploaded.status_code == 201
        assert uploaded.body is not None
        self.document_id = uploaded.body["id"]
        self.probe.release_indexing()
        finished = self._until_terminal(self.token, self.document_id)
        assert finished.body["status"] == "ready"
        self.stored_pieces = self.probe.pieces_for(self.document_id)
        assert self.stored_pieces
        self.piece_writes_before = self.probe.replace_count(self.document_id)
        assert self.piece_writes_before >= 1
        self.fakes.clear_vectors(self.document_id)
        assert self.chats.vectors(self.token, self.document_id).body["texts"] == []
        self.created = self.chats.create(self.token, self.document_id)
        assert self.created.status_code == 201
        assert self.created.body is not None
        self.chat_id = self.created.body["id"]

    def and_the_embedding_call(self, fails: str) -> None:
        self.fakes.fail_embeddings(fails)

    def when_the_person_opens_a_chat_on_that_pdf(self) -> None:
        self.opened = self.chats.get(self.token, self.chat_id)

    def then_the_chat_says_the_material_cannot_be_asked_yet(self) -> None:
        opened = self._opened()
        assert opened.status_code == 200
        assert opened.body is not None
        assert opened.body["askable"] is False
        assert opened.body["notice"] == "Материал пока нельзя спросить."
        assert opened.body["lines"] == []

    def then_the_library_row_stays_ready(self) -> None:
        row = self.documents.read(self.token, self.document_id)
        assert row.status_code == 200
        assert row.body is not None
        assert row.body["status"] == "ready"

    def when_the_embedding_call_succeeds_and_the_person_opens_the_chat_again(self) -> None:
        self.fakes.fail_embeddings(None)
        self.opened = self.chats.get(self.token, self.chat_id)

    def then_the_chat_becomes_askable(self) -> None:
        opened = self._opened()
        assert opened.status_code == 200
        assert opened.body is not None
        assert opened.body["askable"] is True
        assert opened.body["notice"] is None
        found = self.chats.vectors(self.token, self.document_id)
        assert found.status_code == 200
        assert found.body["texts"] == list(self.stored_pieces)
        assert found.body["dimensions"] == [384] * len(self.stored_pieces)

    def then_pieces_already_stored_are_not_stored_again(self) -> None:
        assert self.probe.replace_count(self.document_id) == self.piece_writes_before
        found = self.chats.vectors(self.token, self.document_id)
        assert found.body["texts"] == list(self.stored_pieces)

    def _opened(self):
        assert self.opened is not None
        return self.opened
