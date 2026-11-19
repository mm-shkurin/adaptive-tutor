import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestExaminerPostsTheFirstQuestionWithFourChoices(AbstractBackendTest):
    """Examiner posts the first question with four choices and no page.

    Given a signed-in person with an askable chat
    When the person chooses Examiner
    Then the tutor posts one question immediately
    And the question has four choices
    And the right choice is not marked
    And the question has no page
    """

    def test_should_post_one_question_with_four_unmarked_choices(self, chats):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.when_the_person_chooses_examiner()
        chats.then_the_tutor_posts_one_question_with_four_choices_and_no_page()
