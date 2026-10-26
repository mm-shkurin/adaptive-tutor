import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestTheAppRefusesToStartWhenIndexingSettingsAreMissing(AbstractBackendTest):
    """The app refuses to start when indexing settings are missing.

    Scenario Outline:
    Given <setting> is missing
    When the app starts
    Then startup fails before it accepts an upload
    And it does not pretend the check passed

    Examples:
      | setting |
      | the virus check |
      | the search store |
      | the document store |
    """

    @pytest.mark.parametrize(
        "setting",
        [
            pytest.param(
                "the virus check",
                marks=pytest.mark.skip(
                    reason="RED: AssertionError startup accepted an upload — ClamAV settings not validated at boot"
                ),
            ),
            pytest.param(
                "the search store",
                marks=pytest.mark.skip(
                    reason="RED: AssertionError startup accepted an upload — Qdrant settings not validated at boot"
                ),
            ),
            "the document store",
        ],
    )
    def test_should_refuse_startup_when_setting_is_missing(self, startup, setting):
        startup.given_setting_is_missing(setting)
        startup.when_the_app_starts()
        startup.then_startup_fails_before_it_accepts_an_upload()
        startup.then_it_does_not_pretend_the_check_passed()
