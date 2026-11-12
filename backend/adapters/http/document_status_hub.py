import asyncio
from uuid import UUID

from domain.document.document import Document


class DocumentStatusHub:
    def __init__(self, maxsize: int = 32):
        self._subs: dict[UUID, list[asyncio.Queue]] = {}
        self._maxsize = maxsize

    def subscribe(self, owner_id: UUID) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=self._maxsize)
        self._subs.setdefault(owner_id, []).append(queue)
        return queue

    def unsubscribe(self, owner_id: UUID, queue: asyncio.Queue) -> None:
        queues = self._subs.get(owner_id)
        if queues is None:
            return
        if queue in queues:
            queues.remove(queue)
        if not queues:
            self._subs.pop(owner_id, None)

    def publish(self, owner_id: UUID, document: Document) -> None:
        for queue in list(self._subs.get(owner_id, ())):
            self._offer(queue, document)

    def _offer(self, queue: asyncio.Queue, document: Document) -> None:
        try:
            queue.put_nowait(document)
            return
        except asyncio.QueueFull:
            pass
        try:
            queue.get_nowait()
        except asyncio.QueueEmpty:
            pass
        try:
            queue.put_nowait(document)
        except asyncio.QueueFull:
            pass
