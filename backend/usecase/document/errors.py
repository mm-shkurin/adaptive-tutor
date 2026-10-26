class StoreUnavailable(Exception):
    """The document store could not answer."""


class DocumentNotFound(Exception):
    """No document for this caller, or the caller is not signed in."""


class InvalidDocument(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)
