from statements.reply_statements import NEIGHBOUR_PDF


class EmptyVectorStatements:
    def and_a_neighbour_who_owns_a_ready_pdf_with_vectors(self) -> None:
        self.given_a_signed_in_person()
        opened = self.sessions.open_account("neil@example.test", "Neil")
        assert opened.status_code == 200
        assert opened.body is not None
        neighbour_token = opened.body["access_token"]
        uploaded = self.documents.submit_pdf(neighbour_token, NEIGHBOUR_PDF, self.lecture)
        assert uploaded.status_code == 201
        assert uploaded.body is not None
        self.neighbour_id = uploaded.body["id"]
        self.probe.release_indexing()
        finished = self._until_terminal(neighbour_token, self.neighbour_id)
        assert finished.body["status"] == "ready"
        found = self.chats.vectors(neighbour_token, self.neighbour_id)
        assert found.status_code == 200
        assert found.body["texts"]
        self.neighbour_vectors = found.body
        self.neighbour_token = neighbour_token
        self.neighbour_upserts = self.fakes.upsert_count(self.neighbour_id)

    def when_a_vector_write_is_attempted_with_no_document(self) -> None:
        written = self.chats.write_empty_vectors(self.token)
        assert written.status_code == 204

    def then_no_piece_and_no_vector_is_written(self) -> None:
        assert self.fakes.upsert_count(self.neighbour_id) == self.neighbour_upserts

    def then_the_neighbours_vectors_are_unchanged(self) -> None:
        found = self.chats.vectors(self.neighbour_token, self.neighbour_id)
        assert found.status_code == 200
        assert found.body == self.neighbour_vectors
