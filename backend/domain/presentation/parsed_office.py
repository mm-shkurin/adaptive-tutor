from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedOfficeSlide:
    text: str
    image: bytes | None