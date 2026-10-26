class StoreUnavailable(Exception):
    """The document store could not answer."""


class DocumentNotFound(Exception):
    """No document for this caller, or the caller is not signed in."""


class InvalidDocument(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class RateLimited(Exception):
    code = "rate_limited"
    message = "Too many uploads in this minute"


class RateUnavailable(Exception):
    code = "rate_unavailable"
    message = "Upload limit could not be checked"


class DuplicateSubmission(Exception):
    """Another delivery already claimed this Idempotency-Key for the owner."""
