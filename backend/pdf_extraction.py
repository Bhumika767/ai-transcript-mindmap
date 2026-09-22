import re
from dataclasses import dataclass
from pathlib import Path

import pymupdf


class PdfExtractionError(Exception):
    """Base error for deterministic PDF paragraph extraction."""


class PdfNotFoundError(PdfExtractionError, FileNotFoundError):
    """Raised when the requested PDF path does not exist."""


class InvalidPageNumberError(PdfExtractionError, ValueError):
    """Raised when the requested page number is outside the PDF."""


class InvalidParagraphNumberError(PdfExtractionError, ValueError):
    """Raised when the requested paragraph number is outside the page."""


class PdfReadError(PdfExtractionError):
    """Raised when the PDF cannot be opened or read."""


@dataclass(frozen=True)
class ExtractedParagraph:
    pdf_path: str
    page_number: int
    paragraph_number: int
    text: str

    @property
    def text_length(self) -> int:
        return len(self.text)


def _paragraphs_on_page(page: pymupdf.Page) -> list[str]:
    blocks = page.get_text("dict")["blocks"]
    text_blocks = [block for block in blocks if block["type"] == 0]
    size_counts = {}

    for block in text_blocks:
        for line in block["lines"]:
            for span in line["spans"]:
                size = round(span["size"], 1)
                size_counts[size] = size_counts.get(size, 0) + len(span["text"].strip())

    body_size = max(size_counts, key=lambda size: size_counts[size]) if size_counts else 0
    paragraphs = []

    for block in text_blocks:
        block_text = " ".join(
            span["text"].strip()
            for line in block["lines"]
            for span in line["spans"]
            if span["text"].strip()
        )
        if not block_text:
            continue

        spans = [span for line in block["lines"] for span in line["spans"]]
        block_size = max(round(span["size"], 1) for span in spans)
        is_bold = all("bold" in span["font"].lower() for span in spans)
        is_larger_than_body = body_size and block_size > body_size * 1.15
        is_short_bold_heading = is_bold and len(block_text) <= 100
        is_numbered_heading = re.match(r"^\d+\.\S", block_text) is not None

        if (
            not is_larger_than_body
            and not is_short_bold_heading
            and not is_numbered_heading
        ):
            paragraphs.append(re.sub(r"\s+", " ", block_text))

    return paragraphs


def extract_paragraph(
    pdf_path: str | Path,
    page_number: int,
    paragraph_number: int,
) -> ExtractedParagraph:
    path = Path(pdf_path)
    if not path.is_file():
        raise PdfNotFoundError(f"PDF does not exist: {path}")
    if page_number < 1:
        raise InvalidPageNumberError("Page number must be 1 or greater")
    if paragraph_number < 1:
        raise InvalidParagraphNumberError("Paragraph number must be 1 or greater")

    try:
        document = pymupdf.open(path)
    except Exception as error:
        raise PdfReadError(f"PDF could not be read: {path}") from error

    with document:
        if page_number > document.page_count:
            raise InvalidPageNumberError(
                f"Page {page_number} is outside the PDF "
                f"(pages: {document.page_count})"
            )

        paragraphs = _paragraphs_on_page(document[page_number - 1])
        if paragraph_number > len(paragraphs):
            raise InvalidParagraphNumberError(
                f"Paragraph {paragraph_number} is not available on page "
                f"{page_number} (found {len(paragraphs)})"
            )

        return ExtractedParagraph(
            pdf_path=str(path),
            page_number=page_number,
            paragraph_number=paragraph_number,
            text=paragraphs[paragraph_number - 1],
        )
