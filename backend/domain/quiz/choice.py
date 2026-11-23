from dataclasses import dataclass


@dataclass(frozen=True)
class Choice:
    id: str
    text: str
