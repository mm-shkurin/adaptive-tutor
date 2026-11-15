class ChatNotFound(Exception):
    """No chat for this caller, or the caller is not signed in."""


class NoReadyDocument(Exception):
    """This person has no ready PDF to bind."""


class StoreUnavailable(Exception):
    """The chat store could not answer."""
