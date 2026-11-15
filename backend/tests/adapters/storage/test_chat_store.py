from datetime import datetime, timezone
from uuid import uuid4

import pytest

from adapters.storage.chat_store import PostgresChatStore
from domain.chat.chat import Chat
from domain.document.document import Document


@pytest.mark.asyncio
async def test_should_list_a_chat_bound_to_its_document(sessions, intake):
    owner_id = uuid4()
    document = Document.accepted("older.pdf", 2048).ready(1, 1)
    await intake.store(owner_id, document, b"pdf", str(uuid4()))
    chat = Chat.bound_to(document)
    created_at = datetime(2024, 5, 6, 7, 8, 9, tzinfo=timezone.utc)

    await PostgresChatStore(sessions).add(owner_id, chat, created_at)
    listed = await PostgresChatStore(sessions).list_for(owner_id)

    assert listed == (Chat.stored(chat.id, document.id, "older.pdf"),)
    assert listed[0].preview() is None
    assert listed[0].lines == ()
