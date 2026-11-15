class PartialVectorStatements:
    def and_a_ready_pdf_whose_vector_run_stored_some_pieces_and_then_failed(self) -> None:
        self.and_a_ready_pdf_with_no_vectors()
        assert len(self.stored_pieces) >= 2
        self.failed_ordinal = 1
        upserts_before_open = self.fakes.upsert_count(self.document_id)
        self.fakes.fail_embeddings_after(self.failed_ordinal)
        partial = self.chats.get(self.token, self.chat_id)
        assert partial.status_code == 200
        assert partial.body is not None
        assert partial.body["askable"] is False
        self.partial_notice = partial.body["notice"]
        assert self.partial_notice == "Материал пока нельзя спросить."
        found = self.chats.vectors(self.token, self.document_id)
        assert found.status_code == 200
        assert found.body["texts"] == list(self.stored_pieces[: self.failed_ordinal])
        self.upserts_after_partial = self.fakes.upsert_count(self.document_id)
        assert self.upserts_after_partial - upserts_before_open == self.failed_ordinal

    def when_the_person_opens_the_chat_again_after_a_partial_vector_run(self) -> None:
        self.fakes.fail_embeddings(None)
        self.opened = self.chats.get(self.token, self.chat_id)

    def then_the_pieces_already_stored_are_not_stored_again(self) -> None:
        added = self.fakes.upsert_count(self.document_id) - self.upserts_after_partial
        assert added == len(self.stored_pieces) - self.failed_ordinal
        found = self.chats.vectors(self.token, self.document_id)
        assert found.status_code == 200
        assert len(found.body["texts"]) == len(set(found.body["texts"]))

    def then_the_pieces_after_the_failed_one_are_still_attempted(self) -> None:
        found = self.chats.vectors(self.token, self.document_id)
        assert found.status_code == 200
        assert found.body["texts"] == list(self.stored_pieces)

    def then_the_run_records_which_piece_failed(self) -> None:
        recorded = self.chats.vector_failure(self.token, self.document_id)
        assert recorded.status_code == 200
        assert recorded.body == {"ordinal": self.failed_ordinal}

    def then_the_person_facing_notice_stays_the_fixed_sentence(self) -> None:
        assert self.partial_notice == "Материал пока нельзя спросить."
        for piece in self.stored_pieces:
            assert piece not in self.partial_notice

    def then_the_chat_stays_not_askable_until_the_run_finishes(self) -> None:
        opened = self._opened()
        assert opened.status_code == 200
        assert opened.body is not None
        assert opened.body["askable"] is True
        assert opened.body["notice"] is None
