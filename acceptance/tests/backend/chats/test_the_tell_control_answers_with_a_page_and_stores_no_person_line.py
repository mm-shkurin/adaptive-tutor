import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestTheTellControlAnswersWithAPageAndStoresNoPersonLine(AbstractBackendTest):
    """The tell control answers with a page and stores no person line.

    Given a signed-in person whose tutor is withholding
    When the person uses the tell control
    Then the tutor answers with a page
    And no person line is added
    """

    def test_should_release_with_tell_and_no_person_line(self, chats):
        chats.given_a_signed_in_person_whose_tutor_is_withholding()
        chats.when_the_person_uses_the_tell_control()
        chats.then_the_tutor_answers_with_a_page_and_no_person_line_is_added()
