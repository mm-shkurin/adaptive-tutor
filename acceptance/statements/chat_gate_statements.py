from uuid import uuid4

from statements.reply_statements import MODEL, QUESTION

MISSING_CHAT = {"code": "chat_not_found", "message": "Chat was not found"}
NOT_READY = {"code": "document_not_ready", "message": "Document is not ready"}
INVALID_MODEL = {"code": "invalid_model", "message": "Model is not allowed"}
INVALID_MODE = {"code": "invalid_mode", "message": "Mode is not allowed"}
NOT_ASKABLE = {"code": "not_askable", "message": "Material cannot be asked yet"}


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

    def given_a_person_who_is_not_signed_in(self) -> None:
        self.given_a_signed_in_person()
        self.document_id = self._ready_pdf("guest-gate.pdf")
        created = self.chats.create(self.token, self.document_id)
        assert created.status_code == 201
        assert created.body is not None
        self.chat_id = created.body["id"]
        self.listed_before = self.chats.list(self.token)
        assert self.listed_before.status_code == 200
        self.guest_call = None

    def when_the_person_reads_the_chat_list_without_session(self) -> None:
        self.guest_call = self.chats.list_without_session()

    def when_the_person_reads_a_chat_without_session(self) -> None:
        self.guest_call = self.chats.get_without_session(self.chat_id)

    def when_the_person_starts_a_chat_without_session(self) -> None:
        self.guest_call = self.chats.create_without_session(self.document_id)

    def when_the_person_opens_a_chat_for_a_document_without_session(self) -> None:
        self.guest_call = self.chats.open_without_session(self.document_id)

    def when_the_person_sends_a_line_without_session(self) -> None:
        self.guest_call = self.chats.send_payload(
            None,
            self.chat_id,
            {"text": QUESTION, "model": MODEL, "mode": "professor"},
            str(uuid4()),
        )

    def then_the_refusal_matches_a_missing_chat(self) -> None:
        call = self._guest_call()
        assert call.status_code == 404
        assert call.body == MISSING_CHAT

    def then_nothing_is_stored_after_guest_refusal(self) -> None:
        listed = self.chats.list(self.token)
        assert listed.status_code == 200
        assert listed.body == self.listed_before.body
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        assert opened.body["lines"] == []

    def given_a_signed_in_person_with_a_document_in_state(self, state: str) -> None:
        self.given_a_signed_in_person()
        uploaded = self.documents.submit_pdf(self.token, f"{state}.pdf", self.lecture)
        assert uploaded.status_code == 201
        assert uploaded.body is not None
        self.document_id = uploaded.body["id"]
        self.document_state = state
        if state == "waiting":
            self.document_before = self.documents.read(self.token, self.document_id)
        elif state == "indexing":
            moved = self.documents.move_indexing_status(
                self.token, self.document_id, "indexing"
            )
            assert moved.status_code == 200
            self.document_before = moved
        elif state == "failed":
            indexing = self.documents.move_indexing_status(
                self.token, self.document_id, "indexing"
            )
            assert indexing.status_code == 200
            moved = self.documents.move_indexing_status(
                self.token, self.document_id, "failed"
            )
            assert moved.status_code == 200
            self.document_before = moved
        else:
            self.probe.force_document_status(self.document_id, "corrupted")
            self.document_before = self.documents.read(self.token, self.document_id)
        assert self.document_before.status_code == 200
        assert self.document_before.body is not None
        self.bind_call = None

    def when_the_person_starts_a_chat_on_that_document(self) -> None:
        self.bind_call = self.chats.create(self.token, self.document_id)

    def when_the_person_opens_a_chat_for_that_document(self) -> None:
        self.bind_call = self.chats.open(self.token, self.document_id)

    def then_the_bind_is_refused_because_the_document_is_not_ready(self) -> None:
        call = self._bind_call()
        assert call.status_code == 400
        assert call.body == NOT_READY

    def then_no_chat_is_stored(self) -> None:
        listed = self.chats.list(self.token)
        assert listed.status_code == 200
        assert listed.body == {"chats": []}

    def then_the_document_status_is_unchanged(self) -> None:
        current = self.documents.read(self.token, self.document_id)
        assert current.status_code == 200
        assert current.body is not None
        assert current.body["status"] == self.document_before.body["status"]

    def when_the_person_sends_a_line_with_value(self, value: str) -> None:
        payloads = {
            "a null model": {"text": QUESTION, "model": None, "mode": "professor"},
            "a null mode": {"text": QUESTION, "model": MODEL, "mode": None},
            "a model that is not in the list": {
                "text": QUESTION,
                "model": "not/a-model",
                "mode": "professor",
            },
            "a mode that is not in the list": {
                "text": QUESTION,
                "model": MODEL,
                "mode": "not_a_mode",
            },
            "an empty model": {"text": QUESTION, "model": "", "mode": "professor"},
            "an empty mode": {"text": QUESTION, "model": MODEL, "mode": ""},
        }
        self.sent = self.chats.send_payload(
            self.token, self.chat_id, payloads[value], str(uuid4())
        )
        self.refused_value = value

    def then_the_send_is_refused_for_model_or_mode(self) -> None:
        sent = self._sent()
        assert sent.status_code == 400
        if "model" in self.refused_value:
            assert sent.body == INVALID_MODEL
        else:
            assert sent.body == INVALID_MODE

    def given_a_signed_in_person_whose_chat_cannot_be_asked_yet(self) -> None:
        self.given_a_signed_in_person()
        self.document_id = self._ready_pdf("not-askable.pdf")
        created = self.chats.create(self.token, self.document_id)
        assert created.status_code == 201
        assert created.body is not None
        self.chat_id = created.body["id"]
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        assert opened.body["askable"] is False

    def when_the_person_sends_a_line_while_not_askable(self) -> None:
        self.sent = self.chats.send(
            self.token, self.chat_id, QUESTION, MODEL, "professor", str(uuid4())
        )

    def then_the_send_is_refused_as_not_askable(self) -> None:
        sent = self._sent()
        assert sent.status_code == 409
        assert sent.body == NOT_ASKABLE

    def then_the_thread_has_no_person_line_and_no_tutor_line(self) -> None:
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        assert opened.body["lines"] == []

    def _sent(self):
        assert self.sent is not None
        return self.sent

    def _guest_call(self):
        assert self.guest_call is not None
        return self.guest_call

    def _bind_call(self):
        assert self.bind_call is not None
        return self.bind_call
