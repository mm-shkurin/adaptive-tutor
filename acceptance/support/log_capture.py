import logging


class _BufferHandler(logging.Handler):
    def __init__(self, buffer: list[str]):
        super().__init__()
        self._buffer = buffer

    def emit(self, record: logging.LogRecord) -> None:
        self._buffer.append(self.format(record))


class LogCapture:
    def __init__(self):
        self._lines: list[str] = []
        self._handler = _BufferHandler(self._lines)
        self._handler.setLevel(logging.DEBUG)
        self._attached = False

    def attach(self) -> None:
        if self._attached:
            return
        for name in ("", "uvicorn", "uvicorn.error", "uvicorn.access"):
            logging.getLogger(name).addHandler(self._handler)
        self._attached = True

    def detach(self) -> None:
        if not self._attached:
            return
        for name in ("", "uvicorn", "uvicorn.error", "uvicorn.access"):
            logging.getLogger(name).removeHandler(self._handler)
        self._attached = False

    def clear(self) -> None:
        self._lines.clear()

    def text(self) -> str:
        return "\n".join(self._lines)
