import pytest
from uuid import UUID, uuid4

from adapters.storage.document_intake import PostgresDocumentIntake
from domain.document.document import Document


class TestDocumentIntake:
    """DocumentIntake storage adapter tests.

    Tests the write-through-read flow: store creates a document, get retrieves it,
    save updates document status, next_waiting queues waiting documents.
    """

    @pytest.mark.asyncio
    async def test_should_store_and_retrieve_document(self, intake):
        owner_id = uuid4()
        document = Document.accepted("lecture.pdf", 1024)
        content = b"pdf content"

        await intake.store(owner_id, document, content, str(uuid4()))
        retrieved = await intake.get(owner_id, document.id)

        assert retrieved.id == document.id
        assert retrieved.name == document.name
        assert retrieved.size_bytes == document.size_bytes

    @pytest.mark.asyncio
    async def test_should_store_a_name_that_spans_the_old_varchar_limit(self, intake):
        owner_id = uuid4()
        name = ("я" * 254) + "е\u0301"
        document = Document.accepted(name, 1024)

        await intake.store(owner_id, document, b"pdf content", str(uuid4()))
        retrieved = await intake.get(owner_id, document.id)

        assert retrieved.name == name
        assert retrieved.name != name[:255]
        assert "\ufffd" not in retrieved.name

    @pytest.mark.asyncio
    async def test_should_save_document_status_update(self, intake):
        owner_id = uuid4()
        document = Document.accepted("lecture.pdf", 1024)
        updated = document.indexing()

        await intake.store(owner_id, document, b"content", str(uuid4()))
        await intake.save(updated)
        retrieved = await intake.get(owner_id, document.id)
        assert retrieved.status == "indexing"

    @pytest.mark.asyncio
    async def test_should_return_next_waiting_document(self, intake):
        waiting = Document.accepted("waiting.pdf", 512)
        ready = Document.accepted("ready.pdf", 1024).ready(1, 2)
        owner_id = uuid4()

        await intake.store(owner_id, waiting, b"waiting content", str(uuid4()))
        await intake.store(owner_id, ready, b"ready content", str(uuid4()))

        result = await intake.next_waiting()

        assert result is not None
        retrieved_doc, retrieved_content = result
        assert retrieved_doc.id == waiting.id
        assert retrieved_doc.name == waiting.name
        assert retrieved_doc.size_bytes == waiting.size_bytes
        assert retrieved_doc.status == "waiting"
        assert retrieved_content == b"waiting content"
