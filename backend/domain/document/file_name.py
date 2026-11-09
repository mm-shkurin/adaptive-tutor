import unicodedata

NAME_LIMIT = 255


class DocumentNameError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def canonical_name(raw: str) -> str:
    """Keep or refuse a whole name. Count grapheme bases, never slice mid-letter."""
    composed = unicodedata.normalize("NFC", raw)
    if composed.strip() == "":
        raise DocumentNameError("name_missing")
    if _graphemes(composed) > NAME_LIMIT:
        raise DocumentNameError("name_too_long")
    return composed


def _graphemes(text: str) -> int:
    return sum(1 for char in text if unicodedata.combining(char) == 0)
