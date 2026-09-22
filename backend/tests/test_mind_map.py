import unittest

from hierarchy import HierarchyNode
from mind_map import MindMapInputError, generate_mermaid_mindmap


class MindMapTests(unittest.TestCase):
    def test_simple_root_with_one_topic(self):
        hierarchy = HierarchyNode(
            name="Topics",
            children=[HierarchyNode(name="Software Engineering")],
        )

        self.assertEqual(
            generate_mermaid_mindmap(hierarchy),
            "mindmap\n  root((Topics))\n    Software Engineering",
        )

    def test_topic_with_multiple_children(self):
        hierarchy = HierarchyNode(
            name="Topics",
            children=[
                HierarchyNode(
                    name="Software Engineering",
                    children=[
                        HierarchyNode(name="Requirements"),
                        HierarchyNode(name="Writing Code"),
                    ],
                )
            ],
        )

        result = generate_mermaid_mindmap(hierarchy)

        self.assertIn("      Requirements", result)
        self.assertIn("      Writing Code", result)

    def test_multiple_topics(self):
        hierarchy = HierarchyNode(
            name="Topics",
            children=[HierarchyNode(name="A"), HierarchyNode(name="B")],
        )

        self.assertEqual(
            generate_mermaid_mindmap(hierarchy).splitlines()[2:],
            ["    A", "    B"],
        )

    def test_supports_arbitrary_depth(self):
        hierarchy = HierarchyNode(
            name="Root",
            children=[
                HierarchyNode(
                    name="Level 1",
                    children=[
                        HierarchyNode(
                            name="Level 2",
                            children=[HierarchyNode(name="Level 3")],
                        )
                    ],
                )
            ],
        )

        self.assertEqual(
            generate_mermaid_mindmap(hierarchy).splitlines(),
            ["mindmap", "  root((Root))", "    Level 1", "      Level 2", "        Level 3"],
        )

    def test_preserves_ordering(self):
        hierarchy = HierarchyNode(
            name="Topics",
            children=[
                HierarchyNode(name="First"),
                HierarchyNode(name="Second"),
                HierarchyNode(name="Third"),
            ],
        )

        lines = generate_mermaid_mindmap(hierarchy).splitlines()

        self.assertEqual(lines[2:], ["    First", "    Second", "    Third"])

    def test_preserves_duplicate_nodes(self):
        hierarchy = HierarchyNode(
            name="Topics",
            children=[HierarchyNode(name="Same"), HierarchyNode(name="Same")],
        )

        self.assertEqual(generate_mermaid_mindmap(hierarchy).count("    Same"), 2)

    def test_escapes_special_characters_and_whitespace(self):
        hierarchy = HierarchyNode(
            name="Root (main)",
            children=[HierarchyNode(name=' A [quoted]: "value"\n')],
        )

        result = generate_mermaid_mindmap(hierarchy)

        self.assertIn('root(("Root (main)"))', result)
        self.assertIn('    " A [quoted]: \\"value\\"\\n"', result)

    def test_handles_empty_hierarchy(self):
        self.assertEqual(
            generate_mermaid_mindmap(HierarchyNode(name="Topics")),
            "mindmap\n  root((Topics))",
        )

    def test_rejects_invalid_hierarchy(self):
        with self.assertRaises(MindMapInputError):
            generate_mermaid_mindmap({"name": "Topics", "children": "invalid"})

        with self.assertRaises(MindMapInputError):
            generate_mermaid_mindmap(HierarchyNode(name=" "))


if __name__ == "__main__":
    unittest.main()
