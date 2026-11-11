import asyncio
import threading


class PeakChatHold:
    def __init__(self):
        self._release = threading.Event()
        self._in_flight = 0
        self._lock = threading.Lock()

    def arm(self) -> None:
        self._release.clear()

    def release(self) -> None:
        self._release.set()

    def in_flight(self) -> int:
        with self._lock:
            return self._in_flight

    async def enter(self) -> None:
        with self._lock:
            self._in_flight += 1
        try:
            while not self._release.is_set():
                await asyncio.sleep(0.05)
        finally:
            with self._lock:
                self._in_flight -= 1
