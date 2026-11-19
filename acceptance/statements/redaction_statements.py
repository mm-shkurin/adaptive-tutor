from uuid import uuid4

from statements.failed_reply_statements import REPLY_FAILED
from statements.reply_statements import MODEL, NEIGHBOUR_TEXT, QUESTION

SEEDED_SECRET = "seeded-free-llm-secret-value"
SEEDED_PIECE = "seeded-piece-must-not-leak"


class RedactionStatements:
    def given_a_seeded_secret_piece_and_neighbour_line(self) -> None:
        self.given_a_signed_in_person_with_an_askable_chat()
        self.pieces = ({"text": SEEDED_PIECE, "page": 3},) + tuple(self.pieces[1:])
        seeded = self.chats.seed_search(self.token, self.document_id, self.pieces)
        assert seeded.status_code == 204
        self.and_a_neighbours_pieces_are_in_the_search_store()
        keyed = self.chats.set_model_key(self.token, SEEDED_SECRET)
        assert keyed.status_code == 204

    def and_the_call_fails(self, call: str) -> None:
        if call in {"model call", "embedding call"}:
            armed = self.chats.fail_tutor(self.token)
        elif call == "search":
            armed = self.chats.fail_search(self.token)
        elif call == "reply that misses the latency budget":
            armed = self.chats.hang_tutor(self.token)
        else:
            raise AssertionError(call)
        assert armed.status_code == 204

    def when_the_person_meets_that_failure(self) -> None:
        self.sent = self.chats.send(
            self.token, self.chat_id, QUESTION, MODEL, "professor", str(uuid4())
        )

    def then_the_body_is_the_sanctioned_error_without_leaks(self) -> None:
        assert self.sent.status_code == 200
        assert self.sent.body is not None
        assert self.sent.body["error"] == REPLY_FAILED
        blob = str(self.sent.body)
        assert SEEDED_SECRET not in blob
        assert SEEDED_PIECE not in blob
        assert NEIGHBOUR_TEXT not in blob
        assert "traceback" not in blob.lower()
        assert "ScriptedTutor" not in blob
        assert 'File "' not in blob
        assert set(self.sent.body["error"].keys()) == {"code", "message"}
