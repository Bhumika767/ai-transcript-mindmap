import unittest

from hierarchy import HierarchyInputError, HierarchyNode, build_hierarchy
from topic_extraction import TopicExtractionResult


class HierarchyTests(unittest.TestCase):
    def test_one_topic_without_subtopics(self):
        result = build_hierarchy({"topics": [{"name": "Interviews", "subtopics": []}]})

        self.assertEqual(
            result,
            HierarchyNode(
                name="Topics",
                children=[HierarchyNode(name="Interviews")],
            ),
        )

    def test_one_topic_with_multiple_subtopics(self):
        result = build_hierarchy(
            {
                "topics": [
                    {
                        "name": "Software engineering",
                        "subtopics": ["Requirements", "Writing code"],
                    }
                ]
            }
        )

        self.assertEqual(
            result.model_dump(),
            {
                "name": "Topics",
                "children": [
                    {
                        "name": "Software engineering",
                        "children": [
                            {"name": "Requirements", "children": []},
                            {"name": "Writing code", "children": []},
                        ],
                    }
                ],
            },
        )

    def test_multiple_topics(self):
        result = build_hierarchy(
            {
                "topics": [
                    {"name": "A", "subtopics": ["A1"]},
                    {"name": "B", "subtopics": ["B1"]},
                ]
            }
        )

        self.assertEqual([node.name for node in result.children], ["A", "B"])

    def test_empty_topic_list(self):
        result = build_hierarchy(TopicExtractionResult(topics=[]))

        self.assertEqual(result, HierarchyNode(name="Topics"))

    def test_preserves_order_and_duplicates(self):
        result = build_hierarchy(
            {
                "topics": [
                    {"name": "A", "subtopics": ["Same", "Same"]},
                    {"name": "A", "subtopics": []},
                ]
            }
        )

        self.assertEqual([node.name for node in result.children], ["A", "A"])
        self.assertEqual(
            [node.name for node in result.children[0].children], ["Same", "Same"]
        )

    def test_preserves_word_boundaries_in_labels(self):
        result = build_hierarchy(
            {
                "topics": [
                    {
                        "name": "Software Engineering",
                        "subtopics": ["Software Engineering Interviews"],
                    }
                ]
            }
        )

        self.assertEqual(result.children[0].name, "Software Engineering")
        self.assertEqual(
            result.children[0].children[0].name,
            "Software Engineering Interviews",
        )

    def test_rejects_invalid_input(self):
        with self.assertRaises(HierarchyInputError):
            build_hierarchy({"topics": "not a list"})

        with self.assertRaises(HierarchyInputError):
            build_hierarchy({"topics": []}, root_name=" ")


if __name__ == "__main__":
    unittest.main()
