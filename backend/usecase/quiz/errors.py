class QuizNotFound(Exception):
    """No quiz for this caller, or the caller is not signed in."""


class DuplicateQuizKey(Exception):
    """This Idempotency-Key already stored a quiz."""


class StoreUnavailable(Exception):
    """The quiz store could not answer."""
