import json
import re
from time import perf_counter

from pydantic import BaseModel, ConfigDict, ValidationError

from logging_config import pdf_pipeline_logger as logger
from transcription import TranscriptionService

TOPIC_EXTRACTION_PROMPT = """Extract the meaningful topics from the provided text.

Return ONLY valid JSON in exactly this shape:
{"topics":[{"name":"string","subtopics":["string"]}]}

Rules:
- Use only topics and subtopics supported by the input.
- Keep names concise and avoid excessive fragmentation.
- Do not add outside knowledge, facts, or unrelated topics.
- Preserve the meaning of the input.
- Return {"topics":[]} when no meaningful topic can be identified.
- Do not include Markdown fences or any explanation.
"""

class TopicExtractionError(Exception):
    """Base error for topic extraction."""


class EmptyTopicInputError(TopicExtractionError, ValueError):
    """Raised when the cleaned paragraph is empty."""


class TopicLlmError(TopicExtractionError):
    """Raised when the LLM fails during topic extraction."""


class TopicJsonError(TopicExtractionError, ValueError):
    """Raised when the LLM response is not valid JSON."""


class TopicValidationError(TopicExtractionError, ValueError):
    """Raised when the LLM JSON does not match the topic schema."""


class Topic(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    name: str
    subtopics: list[str]


class TopicExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    topics: list[Topic]


def _remove_json_fence(response: str) -> str:
    fenced = re.fullmatch(r"\s*```(?:json)?\s*(.*?)\s*```\s*", response, re.DOTALL)
    return fenced.group(1).strip() if fenced else response.strip()


def _parse_topic_response(response: str) -> dict:
    try:
        payload = json.loads(_remove_json_fence(response))
    except json.JSONDecodeError as error:
        raise TopicJsonError("LLM returned invalid JSON") from error

    try:
        return TopicExtractionResult.model_validate(payload).model_dump()
    except ValidationError as error:
        raise TopicValidationError("LLM JSON does not match the topic schema") from error


def extract_topics(
    service: TranscriptionService,
    text: str,
) -> dict:
    cleaned_text = text.strip()
    if not cleaned_text:
        raise EmptyTopicInputError("Topic extraction input cannot be empty")

    started_at = perf_counter()
    logger.info(
        "stage=topic_extraction event=start input_length=%d model=%s "
        "token_usage=unavailable",
        len(cleaned_text),
        service.llm_model,
    )

    try:
        response = service.clean_with_llm(
            cleaned_text,
            system_prompt=TOPIC_EXTRACTION_PROMPT,
        )
    except Exception as error:
        logger.exception("stage=topic_extraction event=error reason=llm_failure")
        raise TopicLlmError("Topic extraction LLM call failed") from error

    try:
        result = _parse_topic_response(response)
    except TopicExtractionError:
        logger.exception(
            "stage=topic_extraction event=error reason=response_validation"
        )
        raise

    topic_count = len(result["topics"])
    subtopic_count = sum(len(topic["subtopics"]) for topic in result["topics"])
    logger.info(
        "stage=topic_extraction event=complete input_length=%d topics=%d "
        "subtopics=%d elapsed_ms=%.1f model=%s token_usage=unavailable",
        len(cleaned_text),
        topic_count,
        subtopic_count,
        (perf_counter() - started_at) * 1000,
        service.llm_model,
    )
    return result
