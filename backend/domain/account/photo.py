MAX_PHOTO_BYTES = 10 * 1024 * 1024

_JPEG = b"\xff\xd8\xff"
_PNG = b"\x89PNG\r\n\x1a\n"
_RIFF = b"RIFF"
_WEBP = b"WEBP"


class PhotoNotAllowed(Exception):
    """Bytes that are not a jpeg, png, or webp image."""


class PhotoTooLarge(Exception):
    """An upload past the size the profile will store."""


def photo_type(body: bytes) -> str:
    if len(body) > MAX_PHOTO_BYTES:
        raise PhotoTooLarge()
    if body.startswith(_JPEG):
        return "image/jpeg"
    if body.startswith(_PNG):
        return "image/png"
    if len(body) >= 12 and body[:4] == _RIFF and body[8:12] == _WEBP:
        return "image/webp"
    raise PhotoNotAllowed()
