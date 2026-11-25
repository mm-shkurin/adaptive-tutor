from uuid import UUID

from usecase.presentation.progress_body import build_progress
from usecase.presentation.progress_ports import OwnerActivity, OwnerMaterials


class ProgressNotFound(Exception):
    """No progress for this caller, or the caller is not signed in."""


class GetProgress:
    def __init__(self, materials: OwnerMaterials, activity: OwnerActivity, clock):
        self.materials = materials
        self.activity = activity
        self.clock = clock

    async def read(self, owner_id: UUID, material: UUID | None = None) -> dict:
        if material is not None and await self.materials.owned(owner_id, material) is None:
            raise ProgressNotFound()
        chips = await self.materials.chips(owner_id)
        finishes = await self.activity.quiz_finishes(owner_id)
        sends = await self.activity.chat_person_sends(owner_id)
        return build_progress(chips, finishes, sends, material, self.clock.now())