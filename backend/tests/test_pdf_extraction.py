import tempfile
import unittest
from pathlib import Path

import pymupdf

from pdf_extraction import (
    InvalidPageNumberError,
    InvalidParagraphNumberError,
    PdfNotFoundError,
    extract_paragraph,
)


class PdfExtractionTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.pdf_path = Path(self.temp_dir.name) / "sample.pdf"

        document = pymupdf.open()
        page = document.new_page()
        page.insert_text((72, 36), "1.Section heading")
        page.insert_text(
            (72, 72), "Section heading", fontsize=18, fontname="Helvetica-Bold"
        )
        page.insert_text((72, 144), "First paragraph should be selected.")
        page.insert_text((72, 216), "Second paragraph should not be selected.")
        document.save(self.pdf_path)
        document.close()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_extracts_only_requested_paragraph(self):
        result = extract_paragraph(self.pdf_path, page_number=1, paragraph_number=1)

        self.assertEqual(result.page_number, 1)
        self.assertEqual(result.paragraph_number, 1)
        self.assertEqual(result.text, "First paragraph should be selected.")
        self.assertNotIn("Second paragraph", result.text)
        self.assertEqual(result.text_length, len(result.text))

    def test_excludes_heading_from_paragraph_numbering(self):
        result = extract_paragraph(self.pdf_path, page_number=1, paragraph_number=2)

        self.assertEqual(result.text, "Second paragraph should not be selected.")
        self.assertNotIn("Section heading", result.text)

    def test_rejects_missing_pdf(self):
        with self.assertRaises(PdfNotFoundError):
            extract_paragraph(self.pdf_path.with_name("missing.pdf"), 1, 1)

    def test_rejects_invalid_page(self):
        with self.assertRaises(InvalidPageNumberError):
            extract_paragraph(self.pdf_path, 2, 1)

    def test_rejects_invalid_paragraph(self):
        with self.assertRaises(InvalidParagraphNumberError):
            extract_paragraph(self.pdf_path, 1, 3)


if __name__ == "__main__":
    unittest.main()
