import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestTwoChatsCreatedAtTheSameInstantKeepTheirOrder(AbstractBackendTest):
    """Two chats created at the same instant keep their order.

    Given a signed-in person with two chats created at the same instant
    When the person reads the chat list twice
    Then the two chats stay in the same order
    """

    def test_should_keep_the_same_order_across_list_reads(self, chats):
        chats.given_a_signed_in_person_with_two_chats_created_at_the_same_instant()
        chats.when_the_person_reads_the_chat_list_twice()
        chats.then_the_two_chats_stay_in_the_same_order()
