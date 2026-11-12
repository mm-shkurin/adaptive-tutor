from uuid import uuid4

import pytest

from adapters.document_status.notifying_intake import NotifyingDocumentIntake
from adapters.http.document_status_hub import DocumentStatusHub
from adapters.memory.document_intake import MemoryDocumentIntake
from domain.document.document import Document
from tests.support import build


def test_guest_status_stream_matches_missing_document():
    bundle = build()
    response = bundle.client.get("/api/v1/documents/status-events")
    assert response.status_code == 404
    assert response.json() == {
        "code": "document_not_found",
        "message": "Document was not found",
    }


@pytest.mark.asyncio
async def test_notifying_intake_publishes_store_save_and_claim():
    hub = DocumentStatusHub()
    bodies = {}
    intake = NotifyingDocumentIntake(MemoryDocumentIntake(bodies), hub)
    owner_id = uuid4()
    queue = hub.subscribe(owner_id)
    document = Document.accepted("lecture.pdf", 1_048_576)

    await intake.store(owner_id, document, b"%PDF" + b"x" * 100, str(uuid4()))
    stored = queue.get_nowait()
    assert stored.id == document.id
    assert stored.status == "waiting"

    claimed = await intake.next_waiting()
    assert claimed is not None
    indexing = queue.get_nowait()
    assert indexing.status == "indexing"

    ready = indexing.ready(3, 2)
    await intake.save(ready)
    finished = queue.get_nowait()
    assert finished.status == "ready"
    assert finished.page_count == 3
    assert finished.piece_count == 2
    hub.unsubscribe(owner_id, queue)
