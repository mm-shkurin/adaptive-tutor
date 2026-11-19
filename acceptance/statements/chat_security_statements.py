from uuid import uuid4

from statements.chat_gate_statements import MISSING_CHAT
from statements.reply_statements import MODEL, QUESTION, SCRIPT


class ChatSecurityStatements:
    def given_a_signed_in_person_and_a_neighbour_who_owns_a_chat(self) -> None:
        self.given_a_signed_in_person()
        self.own_document_id = self._ready_pdf("own-sec.pdf")
        neighbour = self.sessions.open_account("neil-sec@example.test", "Neil")
        assert neighbour.status_code == 200
        assert neighbour.body is not None
        self.neighbour_token = neighbour.body["access_token"]
        self.neighbour_document_id = self._ready_pdf(
            "neighbour-sec.pdf", self.neighbour_token
        )
        seeded = self.chats.seed_search(
            self.neighbour_token,
            self.neighbour_document_id,
            ({"text": "neighbour-piece", "page": 1},),
        )
        assert seeded.status_code == 204
        created = self.chats.create(self.neighbour_token, self.neighbour_document_id)
        assert created.status_code == 201
        assert created.body is not None
        self.neighbour_chat_id = created.body["id"]
        scripted = self.chats.script_tutor(self.neighbour_token, SCRIPT)
        assert scripted.status_code == 204
        sent = self.chats.send(
            self.neighbour_token,
            self.neighbour_chat_id,
            QUESTION,
            MODEL,
            "professor",
            "neighbour-setup",
        )
        assert sent.status_code == 200
        self.neighbour_before = self.chats.get(self.neighbour_token, self.neighbour_chat_id)
        assert self.neighbour_before.status_code == 200
        self.idor_call = None

    def given_a_signed_in_person_and_a_neighbour_who_owns_a_ready_pdf(self) -> None:
        self.given_a_signed_in_person()
        self.own_document_id = self._ready_pdf("own-sec-pdf.pdf")
        neighbour = self.sessions.open_account("neil-sec-pdf@example.test", "Neil")
        assert neighbour.status_code == 200
        assert neighbour.body is not None
        self.neighbour_token = neighbour.body["access_token"]
        self.neighbour_document_id = self._ready_pdf(
            "neighbour-only.pdf", self.neighbour_token
        )
        self.neighbour_listed_before = self.chats.list(self.neighbour_token)
        assert self.neighbour_listed_before.status_code == 200
        self.idor_call = None

    def when_the_person_reads_the_neighbours_chat(self) -> None:
        self.idor_call = self.chats.get(self.token, self.neighbour_chat_id)

    def when_the_person_sends_a_line_to_the_neighbours_chat(self) -> None:
        self.idor_call = self.chats.send(
            self.token,
            self.neighbour_chat_id,
            "intrusion",
            MODEL,
            "professor",
            str(uuid4()),
        )

    def when_the_person_starts_a_chat_on_the_neighbours_pdf(self) -> None:
        self.idor_call = self.chats.create(self.token, self.neighbour_document_id)

    def when_the_person_opens_a_chat_for_the_neighbours_pdf(self) -> None:
        self.idor_call = self.chats.open(self.token, self.neighbour_document_id)

    def then_the_idor_refusal_matches_a_missing_chat(self) -> None:
        call = self._idor_call()
        assert call.status_code == 404
        assert call.body == MISSING_CHAT

    def then_nothing_of_the_neighbours_is_stored_or_returned(self) -> None:
        if hasattr(self, "neighbour_chat_id"):
            after = self.chats.get(self.neighbour_token, self.neighbour_chat_id)
            assert after.status_code == 200
            assert after.body == self.neighbour_before.body
            listed = self.chats.list(self.token)
            assert listed.status_code == 200
            assert self.neighbour_chat_id not in [
                row["id"] for row in listed.body["chats"]
            ]
        else:
            own = self.chats.list(self.token)
            assert own.status_code == 200
            assert own.body == {"chats": []}
            neighbour = self.chats.list(self.neighbour_token)
            assert neighbour.status_code == 200
            assert neighbour.body == self.neighbour_listed_before.body

    def and_a_retrieved_piece_whose_text_contains_a_script_and_a_sql_fragment(self) -> None:
        self.hostile_piece = "<script>alert(1)</script>'; DROP TABLE chats;--"
        seeded = self.chats.seed_search(
            self.token,
            self.document_id,
            ({"text": self.hostile_piece, "page": 3},),
        )
        assert seeded.status_code == 204

    def when_the_person_sends_a_line_that_contains_a_script_and_a_sql_fragment(self) -> None:
        self.hostile_line = "<img onerror=alert(1)>'; SELECT * FROM accounts;--"
        scripted = self.chats.script_tutor(self.token, SCRIPT)
        assert scripted.status_code == 204
        self.sent = self.chats.send(
            self.token,
            self.chat_id,
            self.hostile_line,
            MODEL,
            "professor",
            str(uuid4()),
        )

    def then_the_thread_shows_that_hostile_line_unchanged(self) -> None:
        sent = self._sent()
        assert sent.status_code == 200
        assert sent.body is not None
        assert sent.body["lines"][0]["text"] == self.hostile_line
        assert sent.body["lines"][1]["sources"][0]["text"] == self.hostile_piece

    def then_the_chat_list_still_contains_only_this_persons_chats(self) -> None:
        listed = self.chats.list(self.token)
        assert listed.status_code == 200
        assert listed.body is not None
        assert [row["id"] for row in listed.body["chats"]] == [self.chat_id]

    def when_the_person_sends_a_line_that_also_names_server_owned_fields(self) -> None:
        scripted = self.chats.script_tutor(self.token, SCRIPT)
        assert scripted.status_code == 204
        self.sent = self.chats.send_payload(
            self.token,
            self.chat_id,
            {
                "text": QUESTION,
                "model": MODEL,
                "mode": "professor",
                "owner_id": str(uuid4()),
                "page": 99,
                "sources": [{"page": 99, "text": "injected"}],
                "role": "tutor",
                "correct": True,
                "id": str(uuid4()),
                "document_id": str(uuid4()),
            },
            str(uuid4()),
        )

    def then_server_owned_send_fields_are_ignored(self) -> None:
        sent = self._sent()
        assert sent.status_code == 200
        assert sent.body is not None
        tutor = sent.body["lines"][1]
        assert tutor["role"] == "tutor"
        assert tutor["page"] == self.pieces[0]["page"]
        assert tutor["sources"][0]["text"] == self.pieces[0]["text"]
        assert tutor.get("correct") is None
        assert sent.body["lines"][0]["role"] == "person"
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body["document_id"] == self.document_id
        assert opened.body["id"] == self.chat_id

    def given_a_signed_in_person_with_a_ready_pdf(self) -> None:
        self.given_a_signed_in_person()
        self.document_id = self._ready_pdf("mass-assign.pdf")
        self.injected_owner = str(uuid4())
        self.injected_id = str(uuid4())
        self.injected_created_at = "1999-01-01T00:00:00Z"
        self.bind_call = None

    def when_the_person_starts_a_chat_on_that_pdf_naming_server_owned_fields(self) -> None:
        self.bind_call = self.chats.create_payload(
            self.token,
            self._bind_payload_with_server_owned_fields(),
        )

    def when_the_person_opens_a_chat_for_that_pdf_naming_server_owned_fields(self) -> None:
        self.bind_call = self.chats.open_payload(
            self.token,
            self._bind_payload_with_server_owned_fields(),
        )

    def then_server_owned_bind_fields_are_ignored(self) -> None:
        call = self._bind_call()
        assert call.status_code in (200, 201)
        assert call.body is not None
        assert call.body["document_id"] == self.document_id
        assert call.body["id"] != self.injected_id
        assert "owner_id" not in call.body
        assert "owner" not in call.body
        assert "created_at" not in call.body
        assert "role" not in call.body
        assert "preview" not in call.body
        assert call.body["lines"] == []
        listed = self.chats.list(self.token)
        assert listed.status_code == 200
        assert listed.body is not None
        row = next(item for item in listed.body["chats"] if item["id"] == call.body["id"])
        assert row == {
            "id": call.body["id"],
            "document_id": self.document_id,
            "document_name": "mass-assign.pdf",
            "preview": None,
        }

    def _bind_payload_with_server_owned_fields(self) -> dict:
        return {
            "document_id": self.document_id,
            "owner_id": self.injected_owner,
            "owner": self.injected_owner,
            "id": self.injected_id,
            "created_at": self.injected_created_at,
            "role": "tutor",
            "preview": "injected-preview",
        }

    def _bind_call(self):
        assert self.bind_call is not None
        return self.bind_call

    def _idor_call(self):
        assert self.idor_call is not None
        return self.idor_call
