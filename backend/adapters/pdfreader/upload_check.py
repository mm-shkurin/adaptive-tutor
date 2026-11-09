import pymupdf

from usecase.document.errors import InvalidDocument


def reject_unreadable_pdf(content: bytes) -> None:
    document = pymupdf.open(stream=content, filetype="pdf")
    try:
        if document.is_encrypted or document.needs_pass:
            raise InvalidDocument("encrypted_pdf", "PDF is encrypted")
        if not _has_text(document):
            raise InvalidDocument("empty_pdf", "PDF has no text")
    finally:
        document.close()


def _has_text(document) -> bool:
    for index in range(document.page_count):
        if document[index].get_text("text").strip():
            return True
    return False
