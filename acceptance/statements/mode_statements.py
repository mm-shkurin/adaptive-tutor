from uuid import uuid4

from statements.reply_statements import MODEL, QUESTION, SCRIPT

SOCRATIC_QUESTION = "What would you say photosynthesis needs?"
TELL_UNAVAILABLE = {"code": "tell_unavailable", "message": "Nothing is withheld"}
RELEASE = "Photosynthesis needs light, water, and carbon dioxide."


class ModeStatements:
    def when_the_person_sends_a_question_in_socratic_mode(self) -> None:
        scripted = self.chats.script_tutor(self.token, SOCRATIC_QUESTION)
        assert scripted.status_code == 204
        self.sent = self.chats.send(
            self.token, self.chat_id, QUESTION, MODEL, "socratic", str(uuid4())
        )

    def then_the_tutor_stores_a_question_without_page_or_sources(self) -> None:
        sent = self._sent()
        assert sent.status_code == 200
        assert sent.body is not None
        tutor = sent.body["lines"][1]
        assert tutor == {
            "id": tutor["id"],
            "role": "tutor",
            "text": SOCRATIC_QUESTION,
            "model": None,
            "mode": "socratic",
            "kind": "withheld",
            "page": None,
            "sources": [],
        }
        assert sent.body["lines"][0]["role"] == "person"
        assert sent.body["lines"][0]["text"] == QUESTION

    def given_a_signed_in_person_with_an_askable_chat_that_is_not_withholding(self) -> None:
        self.given_a_signed_in_person_with_an_askable_chat()

    def when_the_person_asks_to_be_told(self) -> None:
        self.sent = self.chats.send_payload(
            self.token, self.chat_id, {"tell": True}, str(uuid4())
        )

    def then_the_tell_is_refused(self) -> None:
        sent = self._sent()
        assert sent.status_code == 400
        assert sent.body == TELL_UNAVAILABLE

    def then_the_thread_is_unchanged_after_tell_refusal(self) -> None:
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        assert opened.body["lines"] == []

    def given_a_signed_in_person_whose_tutor_is_withholding(self) -> None:
        self.given_a_signed_in_person_with_an_askable_chat()
        self.when_the_person_sends_a_question_in_socratic_mode()
        assert self._sent().status_code == 200
        self.withheld_before = self.chats.get(self.token, self.chat_id)
        assert self.withheld_before.status_code == 200

    def when_the_person_sends_a_non_empty_try(self) -> None:
        scripted = self.chats.script_tutor(self.token, RELEASE)
        assert scripted.status_code == 204
        self.try_text = "I think it needs sunlight."
        self.sent = self.chats.send(
            self.token, self.chat_id, self.try_text, MODEL, "professor", str(uuid4())
        )

    def when_the_person_sends_a_non_empty_line_that_asks_to_be_told(self) -> None:
        scripted = self.chats.script_tutor(self.token, RELEASE)
        assert scripted.status_code == 204
        self.try_text = "Please tell me the answer now."
        self.sent = self.chats.send(
            self.token, self.chat_id, self.try_text, MODEL, "professor", str(uuid4())
        )

    def then_that_line_is_kept_as_the_try_and_the_tutor_answers_with_a_page(self) -> None:
        sent = self._sent()
        assert sent.status_code == 200
        assert sent.body is not None
        assert sent.body["lines"][0]["role"] == "person"
        assert sent.body["lines"][0]["text"] == self.try_text
        tutor = sent.body["lines"][1]
        assert tutor["kind"] == "reply"
        assert tutor["text"] == RELEASE
        assert tutor["page"] == self.pieces[0]["page"]
        assert tutor["sources"]
        assert tutor["mode"] == "socratic"

    def when_the_person_uses_the_tell_control(self) -> None:
        scripted = self.chats.script_tutor(self.token, RELEASE)
        assert scripted.status_code == 204
        self.sent = self.chats.send_payload(
            self.token, self.chat_id, {"tell": True}, str(uuid4())
        )

    def when_the_person_chooses_examiner(self) -> None:
        scripted = self.chats.script_tutor(self.token, "Which process uses light?")
        assert scripted.status_code == 204
        self.sent = self.chats.send_payload(
            self.token, self.chat_id, {"mode": "examiner"}, str(uuid4())
        )

    def then_the_tutor_posts_one_question_with_four_choices_and_no_page(self) -> None:
        sent = self._sent()
        assert sent.status_code == 200
        assert sent.body is not None
        assert len(sent.body["lines"]) == 1
        tutor = sent.body["lines"][0]
        assert tutor["role"] == "tutor"
        assert tutor["mode"] == "examiner"
        assert tutor["kind"] == "question"
        assert tutor["text"] == "Which process uses light?"
        assert tutor["page"] is None
        assert tutor["sources"] == []
        assert tutor["model"] is None
        assert "correct" not in tutor
        assert "choice_id" not in tutor
        assert len(tutor["choices"]) == 4
        assert [choice["id"] for choice in tutor["choices"]] == ["c1", "c2", "c3", "c4"]
        assert all("text" in choice for choice in tutor["choices"])

    def given_a_signed_in_person_with_an_open_examiner_question(self) -> None:
        self.given_a_signed_in_person_with_an_askable_chat()
        self.when_the_person_chooses_examiner()
        self.then_the_tutor_posts_one_question_with_four_choices_and_no_page()
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        self.thread_before = list(opened.body["lines"])
        self.open_question = opened.body["lines"][-1]

    def when_the_person_sends_a_line_instead_of_a_choice(self) -> None:
        self.sent = self.chats.send(
            self.token, self.chat_id, "I think it is photosynthesis.", MODEL, "professor", str(uuid4())
        )

    def when_the_person_chooses_a_choice_that_is_not_on_the_question(self) -> None:
        self.sent = self.chats.send_payload(
            self.token, self.chat_id, {"choice_id": "not-a-choice"}, str(uuid4())
        )

    def then_the_send_is_refused_for_choice(self, code: str, message: str) -> None:
        sent = self._sent()
        assert sent.status_code == 400
        assert sent.body == {"code": code, "message": message}

    def then_the_question_stays_open_and_no_grade_is_stored(self) -> None:
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        assert opened.body["lines"] == self.thread_before
        assert opened.body["lines"][-1]["kind"] == "question"
        assert not any(line.get("kind") == "grade" for line in opened.body["lines"])

    def given_a_signed_in_person_who_has_graded_fewer_than_two_examiner_questions(self) -> None:
        self.given_a_signed_in_person_with_an_open_examiner_question()

    def and_an_examiner_question_is_open(self) -> None:
        assert self.open_question["kind"] == "question"

    def when_the_person_chooses_the_choice_the_piece_supports(self) -> None:
        scripted = self.chats.script_tutor(self.token, "Which process uses light?")
        assert scripted.status_code == 204
        self.sent = self.chats.send_payload(
            self.token, self.chat_id, {"choice_id": "c1"}, str(uuid4())
        )

    def then_the_grade_is_right_with_the_piece_page_and_one_new_question(self) -> None:
        sent = self._sent()
        assert sent.status_code == 200
        assert sent.body is not None
        assert len(sent.body["lines"]) == 2
        grade = sent.body["lines"][0]
        assert grade["kind"] == "grade"
        assert grade["correct"] is True
        assert grade["choice_id"] == "c1"
        assert grade["page"] == self.pieces[0]["page"]
        assert grade["mode"] == "examiner"
        assert grade["model"] is None
        question = sent.body["lines"][1]
        assert question["kind"] == "question"
        assert len(question["choices"]) == 4
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        grades = [line for line in opened.body["lines"] if line.get("kind") == "grade"]
        assert len(grades) == 1

    def given_a_signed_in_person_with_the_third_examiner_question_open(self) -> None:
        self.given_a_signed_in_person_with_an_open_examiner_question()
        for _ in range(2):
            scripted = self.chats.script_tutor(self.token, "Which process uses light?")
            assert scripted.status_code == 204
            graded = self.chats.send_payload(
                self.token, self.chat_id, {"choice_id": "c1"}, str(uuid4())
            )
            assert graded.status_code == 200
            assert graded.body is not None
            assert graded.body["lines"][-1]["kind"] == "question"
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        self.thread_before = list(opened.body["lines"])
        assert sum(1 for line in opened.body["lines"] if line.get("kind") == "grade") == 2
        assert opened.body["lines"][-1]["kind"] == "question"

    def when_the_person_chooses_a_choice_the_piece_does_not_support(self) -> None:
        self.sent = self.chats.send_payload(
            self.token, self.chat_id, {"choice_id": "c2"}, str(uuid4())
        )

    def then_the_grade_is_wrong_with_the_piece_page_and_no_further_question(self) -> None:
        sent = self._sent()
        assert sent.status_code == 200
        assert sent.body is not None
        assert len(sent.body["lines"]) == 1
        grade = sent.body["lines"][0]
        assert grade["kind"] == "grade"
        assert grade["correct"] is False
        assert grade["choice_id"] == "c2"
        assert grade["page"] == self.pieces[0]["page"]
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        assert sum(1 for line in opened.body["lines"] if line.get("kind") == "grade") == 3
        assert opened.body["lines"][-1]["kind"] == "grade"
        assert not any(
            line.get("kind") == "question" and line["id"] not in {item["id"] for item in self.thread_before}
            for line in opened.body["lines"]
        )

    def given_a_signed_in_person_whose_examiner_question_is_already_graded(self) -> None:
        self.given_a_signed_in_person_with_the_third_examiner_question_open()
        self.when_the_person_chooses_a_choice_the_piece_does_not_support()
        assert self._sent().status_code == 200
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        self.graded_thread = list(opened.body["lines"])
        self.first_grade = next(
            line for line in reversed(opened.body["lines"]) if line.get("kind") == "grade"
        )

    def when_the_person_chooses_again(self) -> None:
        self.sent = self.chats.send_payload(
            self.token, self.chat_id, {"choice_id": "c3"}, str(uuid4())
        )

    def then_the_grade_is_unchanged_and_the_thread_has_one_grade_for_that_question(self) -> None:
        sent = self._sent()
        assert sent.status_code == 200
        assert sent.body is not None
        assert len(sent.body["lines"]) == 1
        assert sent.body["lines"][0]["id"] == self.first_grade["id"]
        assert sent.body["lines"][0]["correct"] == self.first_grade["correct"]
        assert sent.body["lines"][0]["choice_id"] == self.first_grade["choice_id"]
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        assert opened.body["lines"] == self.graded_thread
        assert sum(1 for line in opened.body["lines"] if line.get("kind") == "grade") == 3

    def given_a_signed_in_person_whose_examiner_series_has_three_grades(self) -> None:
        self.given_a_signed_in_person_whose_examiner_question_is_already_graded()

    def when_the_person_sends_a_line_after_examiner_series(self) -> None:
        scripted = self.chats.script_tutor(self.token, SCRIPT)
        assert scripted.status_code == 204
        self.sent = self.chats.send(
            self.token, self.chat_id, QUESTION, MODEL, "professor", str(uuid4())
        )

    def then_no_fourth_question_and_academic_answer_with_page(self) -> None:
        sent = self._sent()
        assert sent.status_code == 200
        assert sent.body is not None
        assert len(sent.body["lines"]) == 2
        assert sent.body["lines"][0]["role"] == "person"
        tutor = sent.body["lines"][1]
        assert tutor["kind"] == "reply"
        assert tutor["mode"] == "professor"
        assert tutor["page"] == self.pieces[0]["page"]
        assert tutor["text"] == SCRIPT
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        questions = [line for line in opened.body["lines"] if line.get("kind") == "question"]
        assert len(questions) == 3
        assert sum(1 for line in opened.body["lines"] if line.get("kind") == "grade") == 3

    def then_the_quiz_list_does_not_contain_the_three_questions(self) -> None:
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        assert all(line.get("kind") != "quiz" for line in opened.body["lines"])

    def when_the_person_chooses_examiner_again(self) -> None:
        self.sent = self.chats.send_payload(
            self.token, self.chat_id, {"mode": "examiner"}, str(uuid4())
        )

    def then_the_open_question_stays_the_only_unanswered_question(self) -> None:
        sent = self._sent()
        assert sent.status_code == 200
        assert sent.body is not None
        assert sent.body["lines"] == []
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        assert opened.body["lines"] == self.thread_before
        pending = None
        for line in opened.body["lines"]:
            if line.get("kind") == "question":
                pending = line
            elif line.get("kind") == "grade":
                pending = None
        assert pending is not None
        assert pending["id"] == self.open_question["id"]

    def given_a_signed_in_person_whose_examiner_series_has_stopped(self) -> None:
        self.given_a_signed_in_person_whose_examiner_series_has_three_grades()
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        self.stopped_thread = list(opened.body["lines"])

    def when_the_person_chooses_examiner_while_stopped(self) -> None:
        self.sent = self.chats.send_payload(
            self.token, self.chat_id, {"mode": "examiner"}, str(uuid4())
        )

    def when_the_person_chooses_a_choice_while_stopped(self) -> None:
        self.sent = self.chats.send_payload(
            self.token, self.chat_id, {"choice_id": "c1"}, str(uuid4())
        )

    def when_the_person_asks_to_be_told_while_stopped(self) -> None:
        self.sent = self.chats.send_payload(
            self.token, self.chat_id, {"tell": True}, str(uuid4())
        )

    def then_the_series_stays_stopped_with_no_new_question_or_grade(self) -> None:
        sent = self._sent()
        assert sent.status_code == 200
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        assert opened.body["lines"] == self.stopped_thread
        assert sum(1 for line in opened.body["lines"] if line.get("kind") == "grade") == 3
        assert sum(1 for line in opened.body["lines"] if line.get("kind") == "question") == 3

    def then_the_tutor_answers_with_a_page_and_no_person_line_is_added(self) -> None:
        sent = self._sent()
        assert sent.status_code == 200
        assert sent.body is not None
        assert len(sent.body["lines"]) == 1
        tutor = sent.body["lines"][0]
        assert tutor["role"] == "tutor"
        assert tutor["kind"] == "reply"
        assert tutor["text"] == RELEASE
        assert tutor["page"] == self.pieces[0]["page"]
        assert tutor["mode"] == "socratic"
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        roles = [line["role"] for line in opened.body["lines"]]
        assert roles == ["person", "tutor", "tutor"]
        assert opened.body["lines"][1]["kind"] == "withheld"
        assert opened.body["lines"][2]["kind"] == "reply"
