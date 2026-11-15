from statements.reply_statements import LECTURE


class VectorReuseStatements:
    def and_a_ready_pdf_that_already_has_vectors(self) -> None:
        uploaded = self.documents.submit_pdf(self.token, LECTURE, self.lecture)
        assert uploaded.status_code == 201
        assert uploaded.body is not None
        self.document_id = uploaded.body["id"]
        self.probe.release_indexing()
        finished = self._until_terminal(self.token, self.document_id)
        assert finished.body["status"] == "ready"
        found = self.chats.vectors(self.token, self.document_id)
        assert found.status_code == 200
        assert found.body["texts"]
        self.upserts_before = self.fakes.upsert_count(self.document_id)
        assert self.upserts_before >= 1
        created = self.chats.create(self.token, self.document_id)
        assert created.status_code == 201
        assert created.body is not None
        self.chat_id = created.body["id"]

    def when_the_person_opens_a_chat_on_that_pdf_twice(self) -> None:
        first = self.chats.get(self.token, self.chat_id)
        second = self.chats.get(self.token, self.chat_id)
        assert first.status_code == 200
        assert second.status_code == 200
        assert first.body["askable"] is True
        assert second.body["askable"] is True

    def then_the_vectors_are_not_written_again(self) -> None:
        assert self.fakes.upsert_count(self.document_id) == self.upserts_before
