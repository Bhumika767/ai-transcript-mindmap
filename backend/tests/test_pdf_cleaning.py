import unittest
from unittest.mock import Mock

from pdf_cleaning import (
    EmptyPdfParagraphError,
    PdfLlmError,
    clean_pdf_paragraph,
    normalize_cleaned_text,
)


class PdfCleaningTests(unittest.TestCase):
    def setUp(self):
        self.service = Mock()
        self.service.llm_model = "gemma3:4b"

    def test_cleans_paragraph_with_existing_llm_service(self):
        self.service.clean_with_llm.return_value = "A clear paragraph."

        result = clean_pdf_paragraph(self.service, "  A  clear paragraph  ")

        self.assertEqual(result, "A clear paragraph.")
        self.service.clean_with_llm.assert_called_once()
        call = self.service.clean_with_llm.call_args
        self.assertEqual(call.args[0], "A  clear paragraph")
        self.assertIn("Return only the cleaned paragraph", call.kwargs["system_prompt"])

    def test_rejects_empty_paragraph(self):
        with self.assertRaises(EmptyPdfParagraphError):
            clean_pdf_paragraph(self.service, "  \n")

        self.service.clean_with_llm.assert_not_called()

    def test_wraps_llm_failure(self):
        self.service.clean_with_llm.side_effect = RuntimeError("Ollama unavailable")

        with self.assertRaises(PdfLlmError):
            clean_pdf_paragraph(self.service, "A paragraph")

    def test_normalizes_missing_word_boundaries_and_punctuation(self):
        result = normalize_cleaned_text(
            "One of the things I have spent a lot of time doingis interviewing software engineers .",
            "One of the things I have spent a lot of time doing is interviewing software engineers.",
        )

        self.assertEqual(
            result,
            "One of the things I have spent a lot of time doing is interviewing software engineers.",
        )


if __name__ == "__main__":
    unittest.main()
