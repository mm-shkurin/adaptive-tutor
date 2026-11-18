import asyncio


class TutorHold:
    def __init__(self):
        self._entered = asyncio.Event()
        self._release = asyncio.Event()

    async def wait(self) -> None:
        self._entered.set()
        await self._release.wait()

    async def until_entered(self) -> None:
        await self._entered.wait()

    def release(self) -> None:
        self._release.set()
