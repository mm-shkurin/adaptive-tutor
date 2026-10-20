class IndexProbe:
    def __init__(self):
        self._pieces: dict[str, tuple[str, ...]] = {}
        self._extracted: dict[str, str] = {}
        self._files: dict[str, bytes] = {}

    def remember_file(self, document_id: str, content: bytes) -> None:
        self._files[document_id] = content

    def remove_file(self, document_id: str) -> None:
        self._files.pop(document_id, None)

    def file_for(self, document_id: str) -> bytes | None:
        return self._files.get(document_id)

    def replace_pieces(self, document_id: str, pieces: tuple[str, ...], extracted: str) -> None:
        self._pieces[document_id] = pieces
        self._extracted[document_id] = extracted

    def pieces_for(self, document_id: str) -> tuple[str, ...]:
        return self._pieces.get(document_id, ())

    def extracted_text(self, document_id: str) -> str:
        return self._extracted.get(document_id, "")
