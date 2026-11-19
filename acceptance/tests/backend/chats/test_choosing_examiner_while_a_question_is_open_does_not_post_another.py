import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestChoosingExaminerWhileAQuestionIsOpenDoesNotPostAnother(AbstractBackendTest):
    """Choosing Examiner while a question is open does not post another.

    Given a signed-in person with an open examiner question
    When the person chooses Examiner again
    Then the open question stays the only unanswered question
    """

    def test_should_keep_the_open_question_only(self, chats):
        chats.given_a_signed_in_person_with_an_open_examiner_question()
        chats.when_the_person_chooses_examiner_again()
        chats.then_the_open_question_stays_the_only_unanswered_question()
