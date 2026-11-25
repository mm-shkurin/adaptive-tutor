from domain.presentation.errors import InvalidOffice
from domain.presentation.parsed_office import ParsedOfficeSlide


class FakeOfficeParser:
    def __init__(self):
        self.source = "pptx"
        self.slides: tuple[ParsedOfficeSlide, ...] = (
            ParsedOfficeSlide("parsed slide one", None),
        )
        self.invalid = False

    def set_slides(self, source: str, slides: tuple[ParsedOfficeSlide, ...]) -> None:
        self.source = source
        self.slides = slides

    def refuse(self) -> None:
        self.invalid = True

    def parse(self, content: bytes) -> tuple[str, tuple[ParsedOfficeSlide, ...]]:
        if self.invalid:
            raise InvalidOffice()
        if not content:
            raise InvalidOffice()
        return self.source, self.slides