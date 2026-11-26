class PresentationNotFound(Exception):
    """No presentation for this caller, or the caller is not signed in."""


class StoreUnavailable(Exception):
    """The presentation store could not answer."""


class OcrUnavailable(Exception):
    """OCR channel failed while indexing a slide."""
