NAME_LIMIT = 60


class NameNotAllowed(Exception):
    """A custom name that is blank or longer than the profile allows."""


def decide_name(raw: str) -> str | None:
    """Empty restores the provider name. A whitespace-only name is refused whole.

    The value is kept or rejected. It is never sliced, so a letter is not cut in half.
    """
    if raw == "":
        return None
    trimmed = raw.strip()
    if not trimmed or len(trimmed) > NAME_LIMIT:
        raise NameNotAllowed()
    return trimmed
