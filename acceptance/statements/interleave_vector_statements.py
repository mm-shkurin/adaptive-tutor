class InterleaveVectorStatements:
    def and_a_ready_pdf_that_is_being_vectorized(self) -> None:
        self.and_a_ready_pdf_with_no_vectors()
        armed = self.chats.arm_vector_interleave(self.token)
        assert armed.status_code == 204

    def when_two_opens_interleave_between_the_read_of_which_pieces_have_vectors_and_the_write(
        self,
    ) -> None:
        self.interleaved = self.chats.interleave_open(self.token, self.chat_id)
        assert self.interleaved.status_code == 200
        assert self.interleaved.body is not None
        opens = self.interleaved.body["opens"]
        assert len(opens) == 2
        assert all(item["askable"] is True for item in opens)

    def then_each_piece_has_one_vector(self) -> None:
        found = self.chats.vectors(self.token, self.document_id)
        assert found.status_code == 200
        assert found.body["texts"] == list(self.stored_pieces)
        assert len(found.body["texts"]) == len(set(found.body["texts"]))
