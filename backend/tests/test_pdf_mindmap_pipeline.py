import json
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import Mock, patch

from hierarchy import HierarchyNode
from mind_map import MindMapInputError
from pdf_extraction import PdfNotFoundError
from pdf_mindmap_pipeline import PdfMindMapResult, process_pdf_to_mind_map


@dataclass
class ExtractedStub:
    pdf_path: str
    page_number: int
    paragraph_number: int
    text: str


class PdfMindMapPipelineTests(unittest.TestCase):
    def setUp(self):
        self.service = Mock()
        self.pdf_path = Path("sample.pdf")
        self.topics = {
            "topics": [
                {
                    "name": "Software Engineering",
                    "subtopics": ["Interviews"],
                }
            ]
        }
        self.hierarchy = HierarchyNode(
            name="Topics",
            children=[
                HierarchyNode(
                    name="Software Engineering",
                    children=[HierarchyNode(name="Interviews")],
                )
            ],
        )

    @patch("pdf_mindmap_pipeline.generate_mermaid_mindmap")
    @patch("pdf_mindmap_pipeline.build_hierarchy")
    @patch("pdf_mindmap_pipeline.extract_topics")
    @patch("pdf_mindmap_pipeline.clean_pdf_paragraph")
    @patch("pdf_mindmap_pipeline.extract_paragraph")
    def test_successful_pipeline_and_stage_chaining(
        self,
        extract_mock,
        clean_mock,
        topics_mock,
        hierarchy_mock,
        mermaid_mock,
    ):
        extract_mock.return_value = ExtractedStub(
            pdf_path=str(self.pdf_path),
            page_number=2,
            paragraph_number=3,
            text="raw paragraph",
        )
        clean_mock.return_value = "clean paragraph"
        topics_mock.return_value = self.topics
        hierarchy_mock.return_value = self.hierarchy
        mermaid_mock.return_value = "mindmap\n  root((Topics))"

        result = process_pdf_to_mind_map(self.service, self.pdf_path, 2, 3)

        extract_mock.assert_called_once_with(self.pdf_path, 2, 3)
        clean_mock.assert_called_once_with(self.service, "raw paragraph")
        topics_mock.assert_called_once_with(self.service, "clean paragraph")
        hierarchy_mock.assert_called_once()
        self.assertEqual(hierarchy_mock.call_args.args[0].model_dump(), self.topics)
        mermaid_mock.assert_called_once_with(self.hierarchy)
        self.assertEqual(result.extracted_text, "raw paragraph")
        self.assertEqual(result.cleaned_text, "clean paragraph")
        self.assertEqual(result.page_number, 2)
        self.assertEqual(result.paragraph_number, 3)
        self.assertEqual(result.hierarchy, self.hierarchy)
        self.assertEqual(result.mermaid, "mindmap\n  root((Topics))")
        self.assertIn('<pre class="mermaid">', result.html)
        self.assertIn("mindmap", result.html)

    @patch("pdf_mindmap_pipeline.extract_paragraph")
    def test_propagates_pdf_extraction_failure(self, extract_mock):
        extract_mock.side_effect = PdfNotFoundError("missing PDF")

        with self.assertRaises(PdfNotFoundError):
            process_pdf_to_mind_map(self.service, "missing.pdf", 1, 1)

    @patch("pdf_mindmap_pipeline.clean_pdf_paragraph")
    @patch("pdf_mindmap_pipeline.extract_paragraph")
    def test_propagates_cleaning_failure(self, extract_mock, clean_mock):
        extract_mock.return_value = ExtractedStub("sample.pdf", 1, 1, "raw")
        clean_mock.side_effect = ValueError("cleaning failed")

        with self.assertRaises(ValueError):
            process_pdf_to_mind_map(self.service, "sample.pdf", 1, 1)

    @patch("pdf_mindmap_pipeline.extract_topics")
    @patch("pdf_mindmap_pipeline.clean_pdf_paragraph")
    @patch("pdf_mindmap_pipeline.extract_paragraph")
    def test_propagates_topic_failure(self, extract_mock, clean_mock, topics_mock):
        extract_mock.return_value = ExtractedStub("sample.pdf", 1, 1, "raw")
        clean_mock.return_value = "clean"
        topics_mock.side_effect = ValueError("topic extraction failed")

        with self.assertRaises(ValueError):
            process_pdf_to_mind_map(self.service, "sample.pdf", 1, 1)

    @patch("pdf_mindmap_pipeline.extract_paragraph")
    def test_invalid_pdf_path_is_rejected(self, extract_mock):
        extract_mock.side_effect = PdfNotFoundError("PDF does not exist")

        with self.assertRaises(PdfNotFoundError):
            process_pdf_to_mind_map(self.service, "not-found.pdf", 1, 1)

    @patch("pdf_mindmap_pipeline.generate_mermaid_mindmap")
    @patch("pdf_mindmap_pipeline.build_hierarchy")
    @patch("pdf_mindmap_pipeline.extract_topics")
    @patch("pdf_mindmap_pipeline.clean_pdf_paragraph")
    @patch("pdf_mindmap_pipeline.extract_paragraph")
    def test_result_serializes_to_dict_and_json(
        self,
        extract_mock,
        clean_mock,
        topics_mock,
        hierarchy_mock,
        mermaid_mock,
    ):
        extract_mock.return_value = ExtractedStub("sample.pdf", 1, 1, "raw")
        clean_mock.return_value = "clean"
        topics_mock.return_value = self.topics
        hierarchy_mock.return_value = self.hierarchy
        mermaid_mock.return_value = "mindmap\n  root((Topics))"

        result = process_pdf_to_mind_map(self.service, "sample.pdf", 1, 1)
        dumped = result.model_dump()
        decoded = json.loads(result.model_dump_json())

        self.assertIsInstance(result, PdfMindMapResult)
        self.assertEqual(dumped["cleaned_text"], "clean")
        self.assertEqual(decoded["mermaid"], "mindmap\n  root((Topics))")
        self.assertGreaterEqual(result.processing_time_ms, 0)

    @patch("pdf_mindmap_pipeline.generate_mermaid_mindmap")
    @patch("pdf_mindmap_pipeline.build_hierarchy")
    @patch("pdf_mindmap_pipeline.extract_topics")
    @patch("pdf_mindmap_pipeline.clean_pdf_paragraph")
    @patch("pdf_mindmap_pipeline.extract_paragraph")
    def test_hierarchy_and_mermaid_failures_are_propagated(
        self,
        extract_mock,
        clean_mock,
        topics_mock,
        hierarchy_mock,
        mermaid_mock,
    ):
        extract_mock.return_value = ExtractedStub("sample.pdf", 1, 1, "raw")
        clean_mock.return_value = "clean"
        topics_mock.return_value = self.topics
        hierarchy_mock.side_effect = ValueError("hierarchy failed")

        with self.assertRaises(ValueError):
            process_pdf_to_mind_map(self.service, "sample.pdf", 1, 1)

        hierarchy_mock.side_effect = None
        hierarchy_mock.return_value = self.hierarchy
        mermaid_mock.side_effect = MindMapInputError("mermaid failed")

        with self.assertRaises(MindMapInputError):
            process_pdf_to_mind_map(self.service, "sample.pdf", 1, 1)


if __name__ == "__main__":
    unittest.main()
