from uuid import UUID

from domain.presentation.errors import FileTooLarge, InvalidImage
from domain.presentation.presentation import Presentation
from usecase.presentation.errors import PresentationNotFound
from usecase.presentation.materials import material_row
from usecase.presentation.ports import PresentationStore, VirusCheck
from usecase.document.ports import DocumentIntake

_MAX_BYTES = 52_428_800
_MAGIC = {
    b"\xff\xd8\xff": "jpeg",
    b"\x89PNG\r\n\x1a\n": "png",
    b"RIFF": "webp",
}


class AddSlides:
    def __init__(
        self,
        presentations: PresentationStore,
        intake: DocumentIntake,
        virus: VirusCheck,
    ):
        self.presentations = presentations
        self.intake = intake
        self.virus = virus

    async def images(self, owner_id: UUID, presentation_id: UUID, key: str, images: tuple[bytes, ...]):
        if not images:
            from domain.presentation.errors import EmptyAdd

            raise EmptyAdd()

        async def build() -> Presentation:
            current = await self._owned(owner_id, presentation_id)
            if current.status != "draft":
                raise PresentationNotFound()
            updated = current
            total_size = 0
            for content in images:
                self._size(content)
                self._kind(content)
                await self.virus.clear(content)
                updated, slide = updated.add_image(content)
                total_size += len(content)
                await self.presentations.put_bytes(owner_id, presentation_id, slide.id, content)
            await self.presentations.save(owner_id, updated)
            await self.intake.upsert(owner_id, material_row(updated, total_size))
            return updated

        return await self.presentations.with_add_key(owner_id, presentation_id, key, build)

    async def _owned(self, owner_id: UUID, presentation_id: UUID) -> Presentation:
        found = await self.presentations.get(owner_id, presentation_id)
        if found is None:
            raise PresentationNotFound()
        return found

    def _size(self, content: bytes) -> None:
        if len(content) > _MAX_BYTES:
            raise FileTooLarge()

    def _kind(self, content: bytes) -> None:
        if any(content.startswith(prefix) for prefix in _MAGIC):
            if content.startswith(b"RIFF") and b"WEBP" not in content[:16]:
                raise InvalidImage()
            return
        raise InvalidImage()