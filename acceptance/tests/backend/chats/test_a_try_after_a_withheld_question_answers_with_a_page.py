import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestATryAfterAWithheldQuestionAnswersWithAPage(AbstractBackendTest):
    """A try after a withheld question answers with a page.

    Scenario Outline:
    Given a signed-in person whose tutor is withholding
    When the person sends <line>
    Then that line is kept as the try
    And the tutor answers with a page
    """

    def test_should_release_on_a_non_empty_try(self, chats):
        chats.given_a_signed_in_person_whose_tutor_is_withholding()
        chats.when_the_person_sends_a_non_empty_try()
        chats.then_that_line_is_kept_as_the_try_and_the_tutor_answers_with_a_page()

    def test_should_release_on_a_line_that_asks_to_be_told(self, chats):
        chats.given_a_signed_in_person_whose_tutor_is_withholding()
        chats.when_the_person_sends_a_non_empty_line_that_asks_to_be_told()
        chats.then_that_line_is_kept_as_the_try_and_the_tutor_answers_with_a_page()
