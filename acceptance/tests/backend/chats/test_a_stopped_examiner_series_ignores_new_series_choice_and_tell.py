import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestAStoppedExaminerSeriesIgnoresNewSeriesChoiceAndTell(AbstractBackendTest):
    """A stopped examiner series ignores a new series, a choice, and tell.

    Given a signed-in person whose examiner series has stopped
    When the person chooses Examiner / chooses a choice / asks to be told
    Then the series stays stopped
    And the thread gains no question and no grade
    """

    def test_should_ignore_choosing_examiner(self, chats):
        chats.given_a_signed_in_person_whose_examiner_series_has_stopped()
        chats.when_the_person_chooses_examiner_while_stopped()
        chats.then_the_series_stays_stopped_with_no_new_question_or_grade()

    def test_should_ignore_a_choice(self, chats):
        chats.given_a_signed_in_person_whose_examiner_series_has_stopped()
        chats.when_the_person_chooses_a_choice_while_stopped()
        chats.then_the_series_stays_stopped_with_no_new_question_or_grade()

    def test_should_ignore_tell(self, chats):
        chats.given_a_signed_in_person_whose_examiner_series_has_stopped()
        chats.when_the_person_asks_to_be_told_while_stopped()
        chats.then_the_series_stays_stopped_with_no_new_question_or_grade()
