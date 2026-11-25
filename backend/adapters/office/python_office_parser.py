from io import BytesIO
from zipfile import BadZipFile, ZipFile

from domain.presentation.errors import InvalidOffice
from domain.presentation.parsed_office import ParsedOfficeSlide


class PythonOfficeParser:
    def parse(self, content: bytes) -> tuple[str, tuple[ParsedOfficeSlide, ...]]:
        kind = _kind(content)
        if kind == "pptx":
            return "pptx", _parse_pptx(content)
        if kind == "docx":
            return "docx", _parse_docx(content)
        raise InvalidOffice()


def _kind(content: bytes) -> str:
    if not content.startswith(b"PK"):
        raise InvalidOffice()
    try:
        with ZipFile(BytesIO(content)) as archive:
            names = set(archive.namelist())
    except BadZipFile as error:
        raise InvalidOffice() from error
    if any(name.startswith("ppt/") for name in names):
        return "pptx"
    if "word/document.xml" in names:
        return "docx"
    raise InvalidOffice()


def _parse_pptx(content: bytes) -> tuple[ParsedOfficeSlide, ...]:
    try:
        from pptx import Presentation
        from pptx.enum.shapes import MSO_SHAPE_TYPE
    except ImportError as error:
        raise InvalidOffice() from error
    try:
        deck = Presentation(BytesIO(content))
    except Exception as error:
        raise InvalidOffice() from error
    if not deck.slides:
        raise InvalidOffice()
    parsed: list[ParsedOfficeSlide] = []
    for slide in deck.slides:
        chunks: list[str] = []
        image = None
        for shape in slide.shapes:
            if shape.shape_type == MSO_SHAPE_TYPE.TABLE:
                chunks.append(_table_text(shape.table))
                continue
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE and image is None:
                image = shape.image.blob
                continue
            text = getattr(shape, "text", "").strip()
            if text:
                chunks.append(text)
        text = "\n\n".join(chunk for chunk in chunks if chunk)
        if text == "" and image is None:
            continue
        parsed.append(ParsedOfficeSlide(text, image))
    if not parsed:
        raise InvalidOffice()
    return tuple(parsed)


def _parse_docx(content: bytes) -> tuple[ParsedOfficeSlide, ...]:
    try:
        from docx import Document
        from docx.oxml.ns import qn
    except ImportError as error:
        raise InvalidOffice() from error
    try:
        doc = Document(BytesIO(content))
    except Exception as error:
        raise InvalidOffice() from error
    parsed: list[ParsedOfficeSlide] = []
    buffer: list[str] = []
    image = _first_docx_image(doc)

    def flush() -> None:
        nonlocal buffer, image
        text = "\n\n".join(buffer).strip()
        if text or image is not None:
            parsed.append(ParsedOfficeSlide(text, image))
        buffer = []
        image = None

    for paragraph in doc.paragraphs:
        if _page_break(paragraph, qn):
            flush()
        text = paragraph.text.strip()
        if text:
            buffer.append(text)
    flush()
    if not parsed:
        text = "\n\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
        image = _first_docx_image(doc)
        if text or image is not None:
            return (ParsedOfficeSlide(text, image),)
        raise InvalidOffice()
    return tuple(parsed)


def _table_text(table) -> str:
    rows: list[str] = []
    for row in table.rows:
        cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
        if cells:
            rows.append(" | ".join(cells))
    return "\n".join(rows)


def _page_break(paragraph, qn) -> bool:
    for run in paragraph.runs:
        for br in run._element.findall(qn("w:br")):
            if br.get(qn("w:type")) == "page":
                return True
    return False


def _first_docx_image(doc) -> bytes | None:
    for part in doc.part.related_parts.values():
        if part.content_type.startswith("image/"):
            return part.blob
    return None