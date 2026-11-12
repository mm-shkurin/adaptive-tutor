import json
import threading
import time

import httpx
import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestStatusEventsFollowUploadWithoutListPoll(AbstractBackendTest):
    """Upload status advances over SSE without polling GET /documents."""

    def test_should_emit_waiting_indexing_ready(self, documents):
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.probe.hold_indexing()
        token = documents.token
        base_url = documents._base_url
        target_id = {"value": None}
        buffered: list[dict] = []
        done = threading.Event()

        def collect():
            with httpx.Client(base_url=base_url, timeout=60) as client:
                with client.stream(
                    "GET",
                    "/api/v1/documents/status-events",
                    headers={"Authorization": f"Bearer {token}"},
                ) as response:
                    assert response.status_code == 200
                    for line in response.iter_lines():
                        if line.startswith("data: "):
                            buffered.append(json.loads(line.removeprefix("data: ")))
                        document_id = target_id["value"]
                        if document_id and any(
                            event["id"] == document_id
                            and event["status"] in {"ready", "failed"}
                            for event in buffered
                        ):
                            done.set()
                            break

        thread = threading.Thread(target=collect, daemon=True)
        thread.start()
        time.sleep(0.2)
        documents.when_the_person_submits_a_valid_pdf()
        target_id["value"] = documents.upload.body["id"]
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and not any(
            event["id"] == target_id["value"] and event["status"] == "waiting"
            for event in buffered
        ):
            time.sleep(0.05)
        assert any(
            event["id"] == target_id["value"] and event["status"] == "waiting"
            for event in buffered
        )
        documents.probe.release_indexing()
        assert done.wait(timeout=30), buffered
        thread.join(timeout=5)
        statuses = [
            event["status"] for event in buffered if event["id"] == target_id["value"]
        ]
        assert "waiting" in statuses
        assert "indexing" in statuses
        assert statuses[-1] == "ready"
