from __future__ import annotations

import tracemalloc
from pathlib import Path
from time import perf_counter

from pydantic import BaseModel, ConfigDict

from hierarchy import HierarchyNode, build_hierarchy
from html_renderer import render_mermaid_html
from logging_config import pdf_pipeline_logger as logger
from mind_map import generate_mermaid_mindmap
from pdf_cleaning import clean_pdf_paragraph
from pdf_extraction import extract_paragraph
from topic_extraction import TopicExtractionResult, extract_topics
from transcription import TranscriptionService


class PdfMindMapResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    source_pdf: str
    page_number: int
    paragraph_number: int
    extracted_text: str
    cleaned_text: str
    topics: TopicExtractionResult
    hierarchy: HierarchyNode
    mermaid: str
    html: str
    processing_time_ms: float


def process_pdf_to_mind_map(
    service: TranscriptionService,
    pdf_path: str | Path,
    page_number: int,
    paragraph_number: int,
) -> PdfMindMapResult:
    started_at = perf_counter()
    tracemalloc.start()
    logger.info(
        "stage=pipeline event=start source=%s page=%d paragraph=%d",
        pdf_path,
        page_number,
        paragraph_number,
    )

    try:
        extracted = extract_paragraph(pdf_path, page_number, paragraph_number)
        logger.info(
            "stage=extraction event=complete source=%s page=%d paragraph=%d "
            "extracted_length=%d",
            extracted.pdf_path,
            extracted.page_number,
            extracted.paragraph_number,
            len(extracted.text),
        )

        cleaned_text = clean_pdf_paragraph(service, extracted.text)
        logger.info(
            "stage=cleaning event=observed input_length=%d output_length=%d",
            len(extracted.text),
            len(cleaned_text),
        )

        topic_data = extract_topics(service, cleaned_text)
        topics = TopicExtractionResult.model_validate(topic_data)
        topic_count = len(topics.topics)
        subtopic_count = sum(len(topic.subtopics) for topic in topics.topics)
        logger.info(
            "stage=topic_extraction event=complete topics=%d subtopics=%d",
            topic_count,
            subtopic_count,
        )

        hierarchy = build_hierarchy(topics)
        logger.info(
            "stage=hierarchy event=complete root=%s child_count=%d",
            hierarchy.name,
            len(hierarchy.children),
        )
        mermaid = generate_mermaid_mindmap(hierarchy)
        logger.info(
            "stage=mermaid event=complete character_count=%d",
            len(mermaid),
        )
        html = render_mermaid_html(mermaid)
        logger.info(
            "stage=html event=complete character_count=%d",
            len(html),
        )
        result = PdfMindMapResult(
            source_pdf=extracted.pdf_path,
            page_number=extracted.page_number,
            paragraph_number=extracted.paragraph_number,
            extracted_text=extracted.text,
            cleaned_text=cleaned_text,
            topics=topics,
            hierarchy=hierarchy,
            mermaid=mermaid,
            html=html,
            processing_time_ms=(perf_counter() - started_at) * 1000,
        )
    except Exception:
        _, peak_bytes = tracemalloc.get_traced_memory()
        logger.exception(
            "stage=pipeline event=error source=%s page=%d paragraph=%d "
            "peak_python_allocated_bytes=%d",
            pdf_path,
            page_number,
            paragraph_number,
            peak_bytes,
        )
        tracemalloc.stop()
        raise

    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    logger.info(
        "stage=pipeline event=complete source=%s topics=%d subtopics=%d "
        "elapsed_ms=%.1f peak_python_allocated_bytes=%d",
        result.source_pdf,
        len(result.topics.topics),
        sum(len(topic.subtopics) for topic in result.topics.topics),
        result.processing_time_ms,
        peak_bytes,
    )
    return result
