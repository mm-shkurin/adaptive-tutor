import unicodedata
from dataclasses import dataclass

from domain.quiz.errors import EmptyTopic, InvalidQuestionCount

TOPIC_LIMIT = 200
ALLOWED_COUNTS = (3, 5, 8)


@dataclass(frozen=True)
class Topic:
    text: str

    @staticmethod
    def parse(raw: object) -> "Topic":
        if not isinstance(raw, str):
            raise EmptyTopic()
        text = unicodedata.normalize("NFC", raw).strip()
        if text == "" or len(text) > TOPIC_LIMIT:
            raise EmptyTopic()
        return Topic(text)


def require_count(raw: object) -> int:
    if type(raw) is not int or raw not in ALLOWED_COUNTS:
        raise InvalidQuestionCount()
    return raw
