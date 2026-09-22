import re
from time import perf_counter

from logging_config import pdf_pipeline_logger as logger
from transcription import TranscriptionService

PDF_CLEANING_PROMPT = """You clean one paragraph extracted from a PDF.

Return only the cleaned paragraph, with no preamble or explanation.
- Fix punctuation, spacing, line-break artifacts, and obvious extraction errors.
- Remove unnecessary filler or redundancy only when clearly appropriate.
- Preserve the original meaning, technical terms, names, and numbers.
- Do not summarize, add information, invent facts, or change the meaning.
"""

class PdfCleaningError(Exception):
    """Base error for PDF paragraph cleaning."""


class EmptyPdfParagraphError(PdfCleaningError, ValueError):
    """Raised when the extracted paragraph is empty."""


class PdfLlmError(PdfCleaningError):
    """Raised when the LLM cannot clean the extracted paragraph."""


def normalize_cleaned_text(cleaned_text: str, source_text: str) -> str:
    """Apply small deterministic formatting repairs to LLM output."""
    normalized = re.sub(r"\s+", " ", cleaned_text).strip()
    normalized = re.sub(r"\s+([,.;:!?])", r"\1", normalized)
    normalized = re.sub(r"([,.;:!?])(?=[A-Za-z])", r"\1 ", normalized)

    source_words = re.findall(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*", source_text)
    for first, second in zip(source_words, source_words[1:]):
        joined = re.escape(first + second)
        replacement = f"{first} {second}"
        normalized = re.sub(
            rf"(?<![A-Za-z0-9]){joined}(?![A-Za-z0-9])",
            replacement,
            normalized,
            flags=re.IGNORECASE,
        )

    return normalized


def clean_pdf_paragraph(
    service: TranscriptionService,
    text: str,
) -> str:
    paragraph = text.strip()
    if not paragraph:
        raise EmptyPdfParagraphError("PDF paragraph cannot be empty")

    started_at = perf_counter()
    logger.info(
        "stage=cleaning event=start input_length=%d model=%s "
        "token_usage=unavailable",
        len(paragraph),
        service.llm_model,
    )

    try:
        cleaned = service.clean_with_llm(
            paragraph,
            system_prompt=PDF_CLEANING_PROMPT,
        )
    except Exception as error:
        logger.exception("stage=cleaning event=error reason=llm_failure")
        raise PdfLlmError("PDF paragraph could not be cleaned") from error

    if not cleaned:
        error = PdfLlmError("LLM returned an empty cleaned paragraph")
        logger.error("stage=cleaning event=error reason=empty_output")
        raise error

    cleaned = normalize_cleaned_text(cleaned, paragraph)

    logger.info(
        "stage=cleaning event=complete input_length=%d output_length=%d "
        "elapsed_ms=%.1f model=%s token_usage=unavailable",
        len(paragraph),
        len(cleaned),
        (perf_counter() - started_at) * 1000,
        service.llm_model,
    )
    return cleaned
