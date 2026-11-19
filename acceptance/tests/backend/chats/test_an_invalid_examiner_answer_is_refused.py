import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestAnInvalidExaminerAnswerIsRefused(AbstractBackendTest):
    """An invalid examiner answer is refused.

    Given a signed-in person with an open examiner question
    When the person sends a line instead of a choice / chooses unknown
    Then the send is refused
    And the question stays open
    And no grade is stored
    """

    def test_should_refuse_a_line_instead_of_a_choice(self, chats):
        chats.given_a_signed_in_person_with_an_open_examiner_question()
        chats.when_the_person_sends_a_line_instead_of_a_choice()
        chats.then_the_send_is_refused_for_choice("choice_required", "Choice is required")
        chats.then_the_question_stays_open_and_no_grade_is_stored()

    def test_should_refuse_a_choice_that_is_not_on_the_question(self, chats):
        chats.given_a_signed_in_person_with_an_open_examiner_question()
        chats.when_the_person_chooses_a_choice_that_is_not_on_the_question()
        chats.then_the_send_is_refused_for_choice(
            "choice_unknown", "Choice is not on the question"
        )
        chats.then_the_question_stays_open_and_no_grade_is_stored()
