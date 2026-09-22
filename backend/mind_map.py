from __future__ import annotations

import json

from pydantic import ValidationError

from hierarchy import HierarchyNode


class MindMapError(Exception):
    """Base error for Mermaid mind-map generation."""


class MindMapInputError(MindMapError, ValueError):
    """Raised when hierarchy data cannot be rendered safely."""


def _validate_hierarchy(hierarchy: HierarchyNode | dict) -> HierarchyNode:
    try:
        result = HierarchyNode.model_validate(hierarchy)
    except ValidationError as error:
        raise MindMapInputError("Hierarchy does not match the expected structure") from error

    def validate_node(node: HierarchyNode) -> None:
        if not node.name.strip():
            raise MindMapInputError("Hierarchy node names cannot be empty")
        for child in node.children:
            validate_node(child)

    validate_node(result)
    return result


def _safe_label(name: str) -> str:
    unsafe_characters = set("()[]\":\r\n")
    if name != name.strip() or any(character in unsafe_characters for character in name):
        return json.dumps(name, ensure_ascii=False)
    return name


def generate_mermaid_mindmap(hierarchy: HierarchyNode | dict) -> str:
    root = _validate_hierarchy(hierarchy)
    lines = ["mindmap", f"  root(({_safe_label(root.name)}))"]

    def append_children(node: HierarchyNode, depth: int) -> None:
        for child in node.children:
            lines.append(f"{'  ' * depth}{_safe_label(child.name)}")
            append_children(child, depth + 1)

    append_children(root, 2)
    return "\n".join(lines)
