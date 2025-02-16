"""Tests for LanguageDetector."""

import unittest
from unittest.mock import Mock, patch

from models.warc_mime_types import ContentType
from models.warc_record import ProcessedWarcRecord, WarcRecord
from processors.language_detector import LanguageDetector


class TestLanguageDetector(unittest.TestCase):
    """Test the language detector processor."""

    def setUp(self):
        """Set up test fixtures."""
        self.detector = LanguageDetector()
        self.mock_record = Mock(spec=WarcRecord)
        self.mock_record.headers = {}

    def test_can_process(self):
        """Test can_process method."""
        test_cases = [
            # Text content types
            (ContentType("text/html"), True),
            (ContentType("text/plain"), True),
            (ContentType("application/json"), True),
            # Non-text content types
            (ContentType("image/jpeg"), False),
            (ContentType("image/png"), False),
            (ContentType("application/pdf"), False),
            (ContentType("application/octet-stream"), False),
        ]

        for content_type, expected in test_cases:
            with self.subTest(content_type=str(content_type)):
                input_obj = Mock()
                input_obj.content_type = content_type
                result = self.detector.can_process(input_obj)
                self.assertEqual(result, expected)

    def test_normalize_language_code(self):
        """Test language code normalization."""
        test_cases = [
            ("en", "en"),
            ("en-US", "en"),
            ("en-GB", "en"),
            ("de-DE", "de"),
            ("sv-SE", "sv"),
            ("EN", "en"),
            ("En-Us", "en"),
            ("  en-GB  ", "en"),
            ("fr-CA", "fr"),
            ("pt-PT", "pt"),
        ]

        for input_code, expected in test_cases:
            with self.subTest(input_code=input_code):
                # pylint: disable=protected-access
                result = self.detector._normalize_language_code(input_code)
                self.assertEqual(result, expected)

    def test_parse_content_language(self):
        """Test Content-Language header parsing."""
        test_cases = [
            ("en-US", ["en"]),
            ("sv-SE, sv, en", ["sv", "en"]),
            ("en-GB, fr-CA", ["en", "fr"]),
            ("de-DE, de, en-US, en", ["de", "en"]),
            ("", []),
            (None, []),
            ("en-US, EN, en-GB", ["en"]),  # Tests deduplication
            ("  en-US,  fr-CA  ", ["en", "fr"]),  # Tests whitespace handling
        ]

        for input_header, expected in test_cases:
            with self.subTest(header=input_header):
                # pylint: disable=protected-access
                result = self.detector._parse_content_language(input_header)
                self.assertEqual(result, expected)

    def test_process_with_content_language_header(self):
        """Test processing when Content-Language header exists."""
        test_cases = [
            # Single language
            ("en-US", {"language": "en", "language_source": "http_header"}),
            # Multiple languages
            (
                "sv-SE, sv, en",
                {
                    "language": "sv",
                    "all_languages": ["sv", "en"],
                    "language_source": "http_header",
                },
            ),
            # Complex case
            (
                "de-DE, de, en-US, en",
                {
                    "language": "de",
                    "all_languages": ["de", "en"],
                    "language_source": "http_header",
                },
            ),
        ]

        for header, expected_metadata in test_cases:
            with self.subTest(header=header):
                # Setup
                self.mock_record.headers = {"Content-Language": header}
                processed_record = ProcessedWarcRecord(
                    record=self.mock_record,
                    processed_content="Some content in multiple languages",
                    metadata={},
                )

                # Process
                self.detector.process(processed_record)

                # Verify metadata
                for key, value in expected_metadata.items():
                    self.assertEqual(processed_record.metadata[key], value)

    @patch("processors.language_detector.detect")
    def test_process_with_language_detection(self, mock_detect):
        """Test processing when language must be detected."""
        # Setup
        self.mock_record.headers = {}  # No Content-Language header
        processed_record = ProcessedWarcRecord(
            record=self.mock_record,
            processed_content="Some English content",
            metadata={},
        )
        mock_detect.return_value = "en"

        # Process
        self.detector.process(processed_record)

        # Verify
        self.assertEqual(processed_record.metadata["language"], "en")
        self.assertEqual(processed_record.metadata["language_source"], "detected")
        self.assertEqual(self.mock_record.headers["Content-Language"], "en")
        mock_detect.assert_called_once_with("Some English content")

    def test_process_empty_content(self):
        """Test processing with empty content."""
        test_cases = [
            "",  # Empty string
            "   ",  # Whitespace only
            None,  # None
        ]

        for content in test_cases:
            with self.subTest(content=content):
                processed_record = ProcessedWarcRecord(
                    record=self.mock_record, processed_content=content, metadata={}
                )

                # Process should return without modifying anything
                self.detector.process(processed_record)
                self.assertEqual(processed_record.metadata, {})
                self.assertEqual(self.mock_record.headers, {})

    @patch("processors.language_detector.detect")
    def test_process_detection_failure(self, mock_detect):
        """Test handling of language detection failures."""
        # Setup
        processed_record = ProcessedWarcRecord(
            record=self.mock_record, processed_content="Some content", metadata={}
        )
        mock_detect.side_effect = ValueError("Detection failed")

        # Process and verify exception
        with self.assertRaises(ValueError):
            self.detector.process(processed_record)

        # Verify no changes were made
        self.assertEqual(processed_record.metadata, {})
        self.assertEqual(self.mock_record.headers, {})


if __name__ == "__main__":
    unittest.main()
