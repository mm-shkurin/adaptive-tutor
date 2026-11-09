import pytest


class TestVirusCheckThatDoesNotClearTheFileAddsNoDocument:
    """A virus check that does not clear the file adds no document.

    Scenario Outline:
    Given a signed-in person with one document
    And the virus check <outcome>
    When the person submits a PDF
    Then the upload is refused
    And the list is unchanged
    And the file is not indexed
    """

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "outcome",
        [
            "finds a virus",
            "times out",
            "answers unreadable",
        ],
    )
    async def test_should_refuse_the_upload_and_leave_the_list_unchanged(
        self, documents, outcome
    ):
        await documents.given_a_signed_in_person()
        await documents.given_a_signed_in_person_with_one_document()
        await documents.given_the_virus_check(outcome)
        await documents.when_the_person_submits_a_pdf()
        await documents.then_the_upload_is_refused_virus()
        await documents.then_the_list_is_unchanged_after_virus_refusal()
        await documents.then_the_file_is_not_indexed_after_virus_refusal()
