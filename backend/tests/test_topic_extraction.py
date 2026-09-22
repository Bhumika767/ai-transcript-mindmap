import json
import unittest
from unittest.mock import Mock

from topic_extraction import (
    EmptyTopicInputError,
    TopicJsonError,
    TopicLlmError,
    TopicValidationError,
    extract_topics,
)


class TopicExtractionTests(unittest.TestCase):
    def setUp(self):
        self.service = Mock()
        self.service.llm_model = "gemma3:4b"

    def test_parses_valid_json(self):
        self.service.clean_with_llm.return_value = json.dumps(
            {
                "topics": [
                    {
                        "name": "Software engineering interviews",
                        "subtopics": ["Interviewing software engineers"],
                    }
                ]
            }
        )

        result = extract_topics(self.service, "Interviewing software engineers.")

        self.assertEqual(result["topics"][0]["name"], "Software engineering interviews")

    def test_parses_multiple_topics_and_subtopics(self):
        self.service.clean_with_llm.return_value = json.dumps(
            {
                "topics": [
                    {"name": "A", "subtopics": ["A1", "A2"]},
                    {"name": "B", "subtopics": ["B1"]},
                ]
            }
        )

        result = extract_topics(self.service, "A and B")

        self.assertEqual(len(result["topics"]), 2)
        self.assertEqual(result["topics"][0]["subtopics"], ["A1", "A2"])

    def test_strips_json_code_fences(self):
        self.service.clean_with_llm.return_value = '```json\n{"topics": []}\n```'

        self.assertEqual(extract_topics(self.service, "Text"), {"topics": []})

    def test_rejects_invalid_json(self):
        self.service.clean_with_llm.return_value = "not json"

        with self.assertRaises(TopicJsonError):
            extract_topics(self.service, "Text")

    def test_rejects_missing_or_invalid_topics(self):
        for response in ["{}", '{"topics": "not a list"}']:
            self.service.clean_with_llm.return_value = response
            with self.assertRaises(TopicValidationError):
                extract_topics(self.service, "Text")

    def test_rejects_empty_input(self):
        with self.assertRaises(EmptyTopicInputError):
            extract_topics(self.service, "  ")

        self.service.clean_with_llm.assert_not_called()

    def test_wraps_llm_failure(self):
        self.service.clean_with_llm.side_effect = RuntimeError("Ollama unavailable")

        with self.assertRaises(TopicLlmError):
            extract_topics(self.service, "Text")


if __name__ == "__main__":
    unittest.main()
