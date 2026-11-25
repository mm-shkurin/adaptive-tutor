class TitleTooLong(Exception):
    """Title exceeds 80 characters after trim."""


class NoSlides(Exception):
    """Index refused: presentation has no slides."""


class TooManySlides(Exception):
    """Index refused: more than 40 slides."""


class SlideLimit(Exception):
    """Adding slides would exceed 40."""


class InvalidImage(Exception):
    """Bytes are not a supported image type."""


class FileTooLarge(Exception):
    """Payload exceeds 50 MB."""


class UnknownSlide(Exception):
    """Patch references a slide that is not on the presentation."""


class InvalidSlideOrder(Exception):
    """slide_order does not list every slide exactly once."""


class TextOnDraftBytes(Exception):
    """Text patch on a draft slide that still has image bytes."""


class PdfNotReady(Exception):
    """PDF is missing, foreign, not kind pdf, or not ready."""


class PdfPageMissing(Exception):
    """Page number is missing, invalid, or beyond the PDF page count."""


class InvalidOffice(Exception):
    """Bytes are not a supported PPTX or DOCX deck."""


class EmptyAdd(Exception):
    """No images or office payload in the add request."""


class InvalidIdempotencyKey(Exception):
    """Idempotency-Key is missing, empty, or too long."""