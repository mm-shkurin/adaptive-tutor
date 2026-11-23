class EmptyTopic(Exception):
    """Topic is empty after trim, or longer than 200 characters."""


class InvalidQuestionCount(Exception):
    """Question count is not 3, 5, or 8."""


class DocumentNotReady(Exception):
    """A quiz binds only a ready PDF."""


class EmptyRetrieval(Exception):
    """The topic matched no piece of the PDF."""


class GenerationFailed(Exception):
    """The model reply could not be stored as a quiz."""


class InvalidChoice(Exception):
    """The choice is not one of the open question's four choices."""


class InvalidIdempotencyKey(Exception):
    """Idempotency-Key is missing, empty, or longer than the allowed maximum."""


class NoOpenAttempt(Exception):
    """Choose and advance need an open attempt."""


class Unanswered(Exception):
    """Next and finish wait for a stored choice."""
