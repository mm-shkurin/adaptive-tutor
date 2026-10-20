class Unauthorized(Exception):
    """A session, code, or account the caller must not be able to tell apart."""


class StoreUnavailable(Exception):
    """The account store could not answer. Callers must not invent an empty profile."""


class OAuthFailed(Exception):
    """The provider refused, timed out, or answered with nothing usable."""
