from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from topic_extraction import TopicExtractionResult


class HierarchyError(Exception):
    """Base error for hierarchy construction."""


class HierarchyInputError(HierarchyError, ValueError):
    """Raised when topic extraction data cannot be validated."""


class HierarchyNode(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    name: str
    children: list[HierarchyNode] = Field(default_factory=list)


def build_hierarchy(
    topic_result: TopicExtractionResult | dict,
    root_name: str = "Topics",
) -> HierarchyNode:
    if not root_name.strip():
        raise HierarchyInputError("Hierarchy root name cannot be empty")

    try:
        validated_result = TopicExtractionResult.model_validate(topic_result)
    except ValidationError as error:
        raise HierarchyInputError(
            "Topic extraction data does not match the expected structure"
        ) from error

    topic_nodes = [
        HierarchyNode(
            name=topic.name,
            children=[HierarchyNode(name=subtopic) for subtopic in topic.subtopics],
        )
        for topic in validated_result.topics
    ]
    return HierarchyNode(name=root_name, children=topic_nodes)
