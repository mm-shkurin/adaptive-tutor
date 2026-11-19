import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestATryAndTheTellControlInterleavedReleaseOnce(AbstractBackendTest):
    """A try and the tell control interleaved release once.

    Given a signed-in person whose tutor is withholding
    When a try and the tell control interleave between the read of the withhold and the write
    Then the tutor answers with a page once
    And the thread has one release
    """

    def test_should_release_once(self, chats):
        chats.given_a_signed_in_person_whose_tutor_is_withholding()
        chats.when_a_try_and_the_tell_control_interleave_between_the_read_of_the_withhold_and_the_write()
        chats.then_the_tutor_answers_with_a_page_once_and_the_thread_has_one_release()
