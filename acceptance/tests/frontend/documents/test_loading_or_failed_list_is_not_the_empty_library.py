import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestLoadingOrFailedListIsNotTheEmptyLibrary(AbstractUiTest):
    """UI Test Scenario 1.3: A list that is loading or that failed to load is not the empty library

    Given a signed-in person opening documents
    When the list is still loading
    Then the screen does not read «Пока нет материалов»
    When the list fails to load
    Then the screen shows an error and a way to try again
    And it does not spin forever
    And it does not read «Пока нет материалов»
    """

    def test_should_show_an_error_and_a_retry_instead_of_the_empty_library(
        self, signed_in_browser, document_library
    ):
        """UI Test Scenario 1.3: A list that is loading or that failed to load is not the empty library

        Given a signed-in person opening documents
        When the list fails to load
        Then the screen shows an error and a way to try again
        And it does not spin forever
        And it does not read «Пока нет материалов»
        """
        signed_in_browser.given_a_signed_in_person_with_no_documents()
        signed_in_browser.given_the_document_list_cannot_be_read()
        document_library.when_the_person_opens_documents_and_the_list_fails()
        document_library.then_the_screen_shows_an_error_and_a_way_to_try_again()
        document_library.then_it_does_not_spin_forever()
        document_library.then_the_screen_does_not_read_no_materials()
        document_library.when_the_person_tries_again()
        document_library.then_the_screen_shows_an_error_and_a_way_to_try_again()
        document_library.then_it_does_not_spin_forever()
        document_library.then_the_screen_does_not_read_no_materials()
