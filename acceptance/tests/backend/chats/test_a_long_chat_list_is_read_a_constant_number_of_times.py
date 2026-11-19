import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestALongChatListIsReadAConstantNumberOfTimes(AbstractBackendTest):
    """A long chat list is read a constant number of times.

    Given a signed-in person with a long list of chats
    When the person reads the chat list
    Then the chat store is read a constant number of times
    And every chat this person owns is listed
    """

    def test_should_read_the_store_once_for_a_long_list(self, chats):
        chats.given_a_signed_in_person_with_a_long_list_of_chats()
        chats.when_the_person_reads_the_chat_list_counting_store_reads()
        chats.then_the_chat_store_is_read_a_constant_number_of_times()
        chats.and_every_chat_this_person_owns_is_listed()
