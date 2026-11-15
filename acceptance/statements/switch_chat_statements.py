from statements.reply_statements import MODEL, QUESTION, SCRIPT


class SwitchChatStatements:
    def given_a_signed_in_person_with_a_chat_that_already_has_a_person_line(self) -> None:
        self.given_a_signed_in_person()
        self.first_document_id = self._ready_pdf("first.pdf")
        self.second_document_id = self._ready_pdf("second.pdf")
        self.second_chat_id = None
        seeded = self.chats.seed_search(
            self.token,
            self.first_document_id,
            ({"text": "first-piece", "page": 1},),
        )
        assert seeded.status_code == 204
        created = self.chats.create(self.token, self.first_document_id)
        assert created.status_code == 201
        assert created.body is not None
        self.previous_chat_id = created.body["id"]
        scripted = self.chats.script_tutor(self.token, SCRIPT)
        assert scripted.status_code == 204
        sent = self.chats.send(
            self.token, self.previous_chat_id, QUESTION, MODEL, "professor", "switch-setup"
        )
        assert sent.status_code == 200
        assert sent.body is not None
        self.previous_lines = list(sent.body["lines"])
        self.opened = None

    def when_the_person_switches_to_a_ready_pdf_that_already_has_a_chat(self) -> None:
        seeded = self.chats.seed_search(
            self.token,
            self.second_document_id,
            ({"text": "second-piece", "page": 2},),
        )
        assert seeded.status_code == 204
        existing = self.chats.create(self.token, self.second_document_id)
        assert existing.status_code == 201
        assert existing.body is not None
        self.second_chat_id = existing.body["id"]
        self.clock.advance(60)
        newer = self.chats.create(self.token, self.second_document_id)
        assert newer.status_code == 201
        assert newer.body is not None
        self.newest_for_second = newer.body["id"]
        self.opened = self.chats.open(self.token, self.second_document_id)

    def when_the_person_switches_to_a_ready_pdf_with_no_chat(self) -> None:
        self.opened = self.chats.open(self.token, self.second_document_id)

    def then_the_previous_chat_still_has_that_person_line(self) -> None:
        previous = self.chats.get(self.token, self.previous_chat_id)
        assert previous.status_code == 200
        assert previous.body is not None
        assert previous.body["id"] == self.previous_chat_id
        assert previous.body["lines"][0]["text"] == self.previous_lines[0]["text"]
        assert previous.body["lines"][0]["role"] == "person"

    def then_the_opened_chat_is_the_newest_chat_for_that_pdf(self) -> None:
        opened = self._opened()
        assert opened.status_code == 200
        assert opened.body is not None
        assert opened.body["id"] == self.newest_for_second
        assert opened.body["document_id"] == self.second_document_id
        assert opened.body["id"] != self.second_chat_id

    def then_the_opened_chat_is_a_new_empty_chat_for_that_pdf(self) -> None:
        opened = self._opened()
        assert opened.status_code == 201
        assert opened.body is not None
        assert opened.body["document_id"] == self.second_document_id
        assert opened.body["lines"] == []
        assert opened.body["id"] != self.previous_chat_id

    def _opened(self):
        assert self.opened is not None
        return self.opened
