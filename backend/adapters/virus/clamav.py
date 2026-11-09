import asyncio
import struct

from usecase.document.errors import InvalidDocument

_CHUNK = 1024 * 1024
_DEADLINE_SECONDS = 30


class ClamavVirusCheck:
    def __init__(self, host: str, port: int, deadline_seconds: float = _DEADLINE_SECONDS):
        self._host = host
        self._port = port
        self._deadline = deadline_seconds

    async def clear(self, content: bytes) -> None:
        try:
            await asyncio.wait_for(self._scan(content), timeout=self._deadline)
        except TimeoutError as error:
            raise InvalidDocument("virus_detected", "Virus detected") from error
        except OSError as error:
            raise InvalidDocument("virus_detected", "Virus detected") from error

    async def _scan(self, content: bytes) -> None:
        reader, writer = await asyncio.open_connection(self._host, self._port)
        try:
            writer.write(b"zINSTREAM\0")
            await writer.drain()
            offset = 0
            while offset < len(content):
                chunk = content[offset : offset + _CHUNK]
                offset += len(chunk)
                writer.write(struct.pack(">I", len(chunk)))
                writer.write(chunk)
                await writer.drain()
            writer.write(struct.pack(">I", 0))
            await writer.drain()
            reply = await reader.read()
        finally:
            writer.close()
            await writer.wait_closed()
        text = reply.replace(b"\0", b"\n").decode("utf-8", "replace")
        if "FOUND" in text or "ERROR" in text:
            raise InvalidDocument("virus_detected", "Virus detected")
        if "OK" not in text:
            raise InvalidDocument("virus_detected", "Virus detected")
