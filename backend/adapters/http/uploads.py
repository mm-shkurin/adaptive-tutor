from fastapi import UploadFile

from domain.account.photo import MAX_PHOTO_BYTES, PhotoTooLarge

_CHUNK = 64 * 1024


async def read_upload(upload: UploadFile) -> bytes:
    """Stop at the size limit. The rest of an oversized upload is not kept."""
    chunks: list[bytes] = []
    size = 0
    while chunk := await upload.read(_CHUNK):
        size += len(chunk)
        if size > MAX_PHOTO_BYTES:
            raise PhotoTooLarge()
        chunks.append(chunk)
    return b"".join(chunks)
