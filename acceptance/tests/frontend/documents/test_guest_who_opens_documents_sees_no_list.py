import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestGuestWhoOpensDocumentsSeesNoList(AbstractUiTest):
    """UI Test Scenario 0.1: A guest who opens documents sees no list

    Given a guest
    When the guest opens documents
    Then the guest sees the landing
    And no document list is shown
    And no upload door is shown
    """

    def test_should_show_the_landing_without_a_list_or_upload_door(
        self, signed_in_browser, document_library
    ):
        """UI Test Scenario 0.1: A guest who opens documents sees no list

        Given a guest
        When the guest opens documents
        Then the guest sees the landing
        And no document list is shown
        And no upload door is shown
        """
        signed_in_browser.given_a_guest()
        document_library.when_the_guest_opens_documents()
        document_library.then_the_guest_sees_the_landing()
        document_library.then_no_document_list_is_shown()
        document_library.then_no_upload_door_is_shown()
