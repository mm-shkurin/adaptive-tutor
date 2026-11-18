from uuid import uuid4

LECTURE = "lecture.pdf"
NEIGHBOUR_PDF = "neighbour.pdf"
QUESTION = "What does the lecture say about photosynthesis?"
MODEL = "qwen/qwen3-32b"
SCRIPT = "Academic answer drawn from the retrieved pages."
NEIGHBOUR_TEXT = "neighbour-only-piece"
NOT_IN_MATERIAL = "Этого нет в материале."
MISSING_QUESTION = "What does the lecture say about unicorn agriculture?"


class ReplyStatements:
    def given_a_signed_in_person_with_an_askable_chat(self) -> None:
        self.given_a_signed_in_person()
        self.document_id = self._ready_pdf(LECTURE)
        self.pieces = tuple(
            {"text": f"piece-{index}", "page": 4 + index} for index in range(12)
        )
        seeded = self.chats.seed_search(self.token, self.document_id, self.pieces)
        assert seeded.status_code == 204
        self.created = self.chats.create(self.token, self.document_id)
        assert self.created is not None
        assert self.created.status_code == 201
        assert self.created.body is not None
        self.chat_id = self.created.body["id"]
        self.sent = None
        self.neighbour_text = NEIGHBOUR_TEXT

    def and_the_pdf_has_more_matching_pieces_than_the_reply_uses_each_with_a_starting_page(self) -> None:
        assert len(self.pieces) > 10
        assert all(isinstance(piece["page"], int) and piece["page"] >= 1 for piece in self.pieces)

    def and_a_neighbours_pieces_are_in_the_search_store(self) -> None:
        opened = self.sessions.open_account("neil@example.test", "Neil")
        assert opened.status_code == 200
        assert opened.body is not None
        neighbour = self._ready_pdf(NEIGHBOUR_PDF, opened.body["access_token"])
        seeded = self.chats.seed_search(
            opened.body["access_token"],
            neighbour,
            ({"text": NEIGHBOUR_TEXT, "page": 2},),
        )
        assert seeded.status_code == 204

    def when_the_person_sends_a_question_naming_a_listed_model_in_professor_mode(self) -> None:
        scripted = self.chats.script_tutor(self.token, SCRIPT)
        assert scripted.status_code == 204
        self.sent = self.chats.send(self.token, self.chat_id, QUESTION, MODEL, "professor", "attempt-1")

    def then_the_tutor_line_arrives_whole(self) -> None:
        sent = self._sent()
        assert sent.status_code == 200
        assert sent.body == {
            "chat_id": self.chat_id,
            "error": None,
            "lines": [self._person_line(sent.body["lines"][0]["id"]), self._tutor_line(sent.body["lines"][1]["id"])],
        }

    def then_the_tone_is_academic(self) -> None:
        tutor = self._tutor()
        assert tutor["mode"] == "professor"
        assert tutor["kind"] == "reply"

    def then_the_model_on_the_line_is_the_model_that_was_asked(self) -> None:
        assert self._tutor()["model"] == MODEL
        calls = self.chats.tutor_calls(self.token)
        assert calls.status_code == 200
        assert calls.body == {
            "calls": [
                {
                    "model": MODEL,
                    "mode": "professor",
                    "question": QUESTION,
                    "sources": [dict(piece) for piece in self.pieces[:10]],
                }
            ]
        }

    def then_the_page_is_the_starting_page_of_the_first_retrieved_piece(self) -> None:
        assert self._tutor()["page"] == self.pieces[0]["page"]

    def then_the_sources_are_only_pieces_of_this_pdf(self) -> None:
        assert [source["text"] for source in self._tutor()["sources"]] == [
            piece["text"] for piece in self.pieces[:10]
        ]

    def then_none_of_the_neighbours_pieces_are_sources(self) -> None:
        assert self.neighbour_text not in [source["text"] for source in self._tutor()["sources"]]

    def then_there_are_at_most_ten_sources(self) -> None:
        sources = self._tutor()["sources"]
        assert len(sources) == 10
        assert len(sources) < len(self.pieces)
        assert self._tutor()["page"] == sources[0]["page"]

    def then_each_source_shows_that_pieces_text_and_starting_page(self) -> None:
        assert self._tutor()["sources"] == [
            {"page": piece["page"], "text": piece["text"]} for piece in self.pieces[:10]
        ]

    def then_the_citation_is_a_page_not_a_slide(self) -> None:
        tutor = self._tutor()
        assert isinstance(tutor["page"], int)
        assert "slide" not in tutor
        assert all("slide" not in source for source in tutor["sources"])

    def and_the_question_matches_nothing_in_this_pdf(self) -> None:
        seeded = self.chats.seed_search(self.token, self.document_id, ())
        assert seeded.status_code == 204

    def when_the_person_sends_the_missing_question(self) -> None:
        self.sent = self.chats.send(
            self.token, self.chat_id, MISSING_QUESTION, MODEL, "professor", str(uuid4())
        )

    def then_the_tutor_says_it_is_not_in_the_material(self) -> None:
        tutor = self._tutor()
        assert tutor["text"] == NOT_IN_MATERIAL
        assert tutor["kind"] == "reply"
        assert tutor["mode"] == "professor"

    def then_the_sources_are_empty(self) -> None:
        assert self._tutor()["sources"] == []
        assert self._tutor()["page"] is None

    def then_the_model_did_not_answer(self) -> None:
        assert self._tutor()["model"] is None
        calls = self.chats.tutor_calls(self.token)
        assert calls.status_code == 200
        assert calls.body["calls"] == []

    def when_the_person_delivers_the_same_attempt_twice(self) -> None:
        scripted = self.chats.script_tutor(self.token, SCRIPT)
        assert scripted.status_code == 204
        key = "attempt-same-twice"
        first = self.chats.send(self.token, self.chat_id, QUESTION, MODEL, "professor", key)
        second = self.chats.send(self.token, self.chat_id, QUESTION, MODEL, "professor", key)
        assert first.status_code == 200
        assert second.status_code == 200
        self.sent = second
        self.first_sent = first

    def then_the_thread_contains_one_person_line_and_one_tutor_line(self) -> None:
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        roles = [line["role"] for line in opened.body["lines"]]
        assert roles == ["person", "tutor"]
        assert self.sent.body["lines"] == self.first_sent.body["lines"]

    def then_the_model_is_called_once(self) -> None:
        calls = self.chats.tutor_calls(self.token)
        assert calls.status_code == 200
        assert len(calls.body["calls"]) == 1

    def when_the_person_sends_a_line_and_omits_the_model_and_the_mode(self) -> None:
        scripted = self.chats.script_tutor(self.token, SCRIPT)
        assert scripted.status_code == 204
        self.sent = self.chats.send_payload(
            self.token, self.chat_id, {"text": QUESTION}, str(uuid4())
        )

    def then_the_tutor_lines_model_is_auto(self) -> None:
        assert self._tutor()["model"] == "auto"

    def then_the_turn_is_professor(self) -> None:
        tutor = self._tutor()
        assert tutor["mode"] == "professor"
        assert tutor["kind"] == "reply"

    def _sent(self):
        assert self.sent is not None
        assert self.sent.body is not None
        return self.sent

    def _tutor(self) -> dict:
        return self._sent().body["lines"][1]

    def _person_line(self, line_id: str) -> dict:
        return {
            "id": line_id,
            "role": "person",
            "text": QUESTION,
            "model": None,
            "mode": None,
            "kind": None,
            "page": None,
            "sources": [],
        }

    def _tutor_line(self, line_id: str) -> dict:
        return {
            "id": line_id,
            "role": "tutor",
            "text": SCRIPT,
            "model": MODEL,
            "mode": "professor",
            "kind": "reply",
            "page": self.pieces[0]["page"],
            "sources": [{"page": piece["page"], "text": piece["text"]} for piece in self.pieces[:10]],
        }
