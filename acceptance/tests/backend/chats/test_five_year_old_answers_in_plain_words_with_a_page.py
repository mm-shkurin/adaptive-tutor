import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestFiveYearOldAnswersInPlainWordsWithAPage(AbstractBackendTest):
    """Five-year-old answers in plain words with a page.

    Given a signed-in person with an askable chat
    And the retrieved piece has a starting page
    When the person sends a question as a five-year-old
    Then the tutor answers in plain words
    And the line has that page
    """

    def test_should_answer_as_five_year_old_with_page(self, chats):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.when_the_person_sends_a_question_as_a_five_year_old()
        chats.then_the_tutor_answers_in_plain_words_with_that_page()
