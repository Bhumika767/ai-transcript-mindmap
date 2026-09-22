import logging
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import Mock, patch

from hierarchy import HierarchyNode
from logging_config import PDF_PIPELINE_LOGGER_NAME
from pdf_mindmap_pipeline import process_pdf_to_mind_map


@dataclass
class ExtractedStub:
    pdf_path: str
    page_number: int
    paragraph_number: int
    text: str


class LoggingObservabilityTests(unittest.TestCase):
    @patch("pdf_mindmap_pipeline.render_mermaid_html", return_value="<html>")
    @patch("pdf_mindmap_pipeline.generate_mermaid_mindmap", return_value="mindmap")
    @patch("pdf_mindmap_pipeline.build_hierarchy")
    @patch("pdf_mindmap_pipeline.extract_topics", return_value={"topics": []})
    @patch("pdf_mindmap_pipeline.clean_pdf_paragraph", return_value="clean text")
    @patch("pdf_mindmap_pipeline.extract_paragraph")
    def test_pipeline_logs_stage_metadata(
        self,
        extract_mock,
        _clean_mock,
        _topics_mock,
        hierarchy_mock,
        _mermaid_mock,
        _html_mock,
    ):
        extract_mock.return_value = ExtractedStub("sample.pdf", 1, 2, "raw text")
        hierarchy_mock.return_value = HierarchyNode(name="Topics")

        with self.assertLogs(PDF_PIPELINE_LOGGER_NAME, level=logging.INFO) as captured:
            process_pdf_to_mind_map(Mock(), Path("sample.pdf"), 1, 2)

        output = "\n".join(captured.output)
        self.assertIn("stage=extraction", output)
        self.assertIn("extracted_length=8", output)
        self.assertIn("stage=cleaning", output)
        self.assertIn("stage=topic_extraction", output)
        self.assertIn("stage=hierarchy", output)
        self.assertIn("stage=mermaid", output)
        self.assertIn("stage=html", output)
        self.assertIn("peak_python_allocated_bytes=", output)
        self.assertIn("elapsed_ms=", output)

    @patch("pdf_mindmap_pipeline.extract_paragraph")
    def test_pipeline_logs_errors_with_stage_context(self, extract_mock):
        extract_mock.side_effect = ValueError("bad PDF")

        with self.assertLogs(PDF_PIPELINE_LOGGER_NAME, level=logging.ERROR) as captured:
            with self.assertRaises(ValueError):
                process_pdf_to_mind_map(Mock(), "sample.pdf", 1, 1)

        output = "\n".join(captured.output)
        self.assertIn("stage=pipeline event=error", output)
        self.assertIn("peak_python_allocated_bytes=", output)


if __name__ == "__main__":
    unittest.main()
