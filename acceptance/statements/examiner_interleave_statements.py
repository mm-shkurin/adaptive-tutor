from statements.examiner_statements import EXAMINER_PROMPT


class ExaminerInterleaveStatements:
    def when_two_choices_interleave_between_the_read_of_the_question_and_the_write(self) -> None:
        scripted = self.chats.script_tutor(self.token, EXAMINER_PROMPT)
        assert scripted.status_code == 204
        armed = self.chats.arm_thread_interleave(self.token)
        assert armed.status_code == 204
        self.interleaved = self.chats.interleave_sends(
            self.token,
            self.chat_id,
            [
                {"key": "choice-a", "payload": {"choice_id": "c1"}},
                {"key": "choice-b", "payload": {"choice_id": "c2"}},
            ],
        )

    def then_the_thread_has_one_grade(self) -> None:
        assert self.interleaved.status_code == 200
        assert self.interleaved.body is not None
        grades = [
            line for line in self.interleaved.body["thread"]["lines"] if line.get("kind") == "grade"
        ]
        assert len(grades) == 1

    def given_two_stale_copies_of_that_question(self) -> None:
        assert self.chats.get(self.token, self.chat_id).status_code == 200

    def when_each_copy_saves_a_different_choice(self) -> None:
        self.when_two_choices_interleave_between_the_read_of_the_question_and_the_write()

    def then_the_thread_has_one_grade_and_the_second_save_does_not_add_another(self) -> None:
        self.then_the_thread_has_one_grade()
        opened = self.chats.get(self.token, self.chat_id)
        assert opened.status_code == 200
        assert opened.body is not None
        grades = [line for line in opened.body["lines"] if line.get("kind") == "grade"]
        assert len(grades) == 1
