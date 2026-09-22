import io
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pymupdf
from fastapi.testclient import TestClient

import app
from hierarchy import HierarchyNode
from pdf_mindmap_pipeline import PdfMindMapResult
from topic_extraction import TopicExtractionResult


class PdfMindMapApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        document = pymupdf.open()
        page = document.new_page()
        page.insert_text((72, 72), "A test paragraph for the PDF endpoint.")
        cls.pdf_bytes = document.tobytes()
        document.close()

    def setUp(self):
        self.original_service = app.service
        app.service = Mock()
        self.client = TestClient(app.app)

    def tearDown(self):
        app.service = self.original_service

    def _upload(self, **overrides):
        data = {"page_number": "1", "paragraph_number": "1"}
        data.update(overrides)
        return self.client.post(
            "/api/pdf-mindmap",
            files={
                "file": (
                    "sample.pdf",
                    io.BytesIO(self.pdf_bytes),
                    "application/pdf",
                )
            },
            data=data,
        )

    def test_existing_endpoints_remain_available(self):
        app.service.get_default_system_prompt.return_value = "prompt"
        app.service.transcribe.return_value = "raw audio text"
        app.service.clean_with_llm.return_value = "clean text"

        status = self.client.get("/api/status")
        prompt = self.client.get("/api/system-prompt")
        transcribe = self.client.post(
            "/api/transcribe",
            files={"audio": ("sample.webm", b"audio", "audio/webm")},
        )
        clean = self.client.post(
            "/api/clean",
            json={"text": "raw text"},
        )

        self.assertEqual(status.status_code, 200)
        self.assertEqual(prompt.json(), {"default_prompt": "prompt"})
        self.assertEqual(transcribe.json(), {"success": True, "text": "raw audio text"})
        self.assertEqual(clean.json(), {"success": True, "text": "clean text"})

    @patch("app.process_pdf_to_mind_map")
    def test_valid_upload_returns_complete_result(self, pipeline_mock):
        pipeline_mock.return_value = PdfMindMapResult(
            source_pdf="temporary.pdf",
            page_number=1,
            paragraph_number=1,
            extracted_text="raw paragraph",
            cleaned_text="clean paragraph",
            topics=TopicExtractionResult(
                topics=[{"name": "Topic", "subtopics": ["Subtopic"]}]
            ),
            hierarchy=HierarchyNode(
                name="Topics",
                children=[
                    HierarchyNode(
                        name="Topic", children=[HierarchyNode(name="Subtopic")]
                    )
                ],
            ),
            mermaid="mindmap\n  root((Topics))",
            html="<!doctype html><pre class=\"mermaid\">mindmap</pre>",
            processing_time_ms=1.0,
        )

        response = self._upload()

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["page_number"], 1)
        self.assertEqual(body["paragraph_number"], 1)
        self.assertEqual(body["source_pdf"], "sample.pdf")
        self.assertEqual(body["extracted_text"], "raw paragraph")
        self.assertEqual(body["cleaned_text"], "clean paragraph")
        self.assertIn("topics", body)
        self.assertIn("hierarchy", body)
        self.assertIn("mermaid", body)
        self.assertIn("html", body)
        pipeline_mock.assert_called_once()

    @patch("app.process_pdf_to_mind_map")
    def test_preserves_page_and_paragraph_numbers(self, pipeline_mock):
        pipeline_mock.return_value = PdfMindMapResult(
            source_pdf="temporary.pdf",
            page_number=3,
            paragraph_number=2,
            extracted_text="raw",
            cleaned_text="clean",
            topics={"topics": []},
            hierarchy={"name": "Topics", "children": []},
            mermaid="mindmap\n  root((Topics))",
            html="<!doctype html><pre class=\"mermaid\">mindmap</pre>",
            processing_time_ms=1.0,
        )

        response = self._upload(page_number="3", paragraph_number="2")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(pipeline_mock.call_args.args[2:], (3, 2))

    @patch("app.process_pdf_to_mind_map")
    def test_temporary_upload_is_cleaned_up(self, pipeline_mock):
        observed_path = None

        def capture_path(service, pdf_path, page_number, paragraph_number):
            nonlocal observed_path
            observed_path = Path(pdf_path)
            self.assertTrue(observed_path.exists())
            return PdfMindMapResult(
                source_pdf=str(observed_path),
                page_number=page_number,
                paragraph_number=paragraph_number,
                extracted_text="raw",
                cleaned_text="clean",
                topics={"topics": []},
                hierarchy={"name": "Topics", "children": []},
                mermaid="mindmap\n  root((Topics))",
                html="<!doctype html><pre class=\"mermaid\">mindmap</pre>",
                processing_time_ms=1.0,
            )

        pipeline_mock.side_effect = capture_path

        response = self._upload()

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(observed_path)
        self.assertFalse(observed_path.exists())

    def test_missing_file_is_rejected(self):
        response = self.client.post(
            "/api/pdf-mindmap",
            data={"page_number": "1", "paragraph_number": "1"},
        )

        self.assertEqual(response.status_code, 422)

    def test_empty_upload_is_rejected(self):
        response = self.client.post(
            "/api/pdf-mindmap",
            files={"file": ("empty.pdf", b"", "application/pdf")},
            data={"page_number": "1", "paragraph_number": "1"},
        )

        self.assertEqual(response.status_code, 400)

    def test_non_pdf_upload_is_rejected(self):
        response = self.client.post(
            "/api/pdf-mindmap",
            files={"file": ("sample.txt", b"text", "text/plain")},
            data={"page_number": "1", "paragraph_number": "1"},
        )

        self.assertEqual(response.status_code, 400)

    def test_invalid_page_and_paragraph_are_rejected(self):
        for field in ("page_number", "paragraph_number"):
            response = self._upload(**{field: "0"})
            self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
