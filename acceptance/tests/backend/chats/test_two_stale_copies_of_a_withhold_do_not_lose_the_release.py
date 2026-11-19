import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestTwoStaleCopiesOfAWithholdDoNotLoseTheRelease(AbstractBackendTest):
    """Two stale copies of a withhold do not lose the release.

    Given a signed-in person whose tutor is withholding
    And two stale copies of that withhold
    When one copy is released by a try and the other by the tell control
    Then one release is kept
    And the second save does not drop that release
    """

    def test_should_keep_one_release(self, chats):
        chats.given_a_signed_in_person_whose_tutor_is_withholding()
        chats.given_two_stale_copies_of_that_withhold()
        chats.when_one_copy_is_released_by_a_try_and_the_other_by_the_tell_control()
        chats.then_one_release_is_kept_and_the_second_save_does_not_drop_it()
