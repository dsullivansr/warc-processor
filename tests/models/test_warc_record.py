"""Tests for WARC record models.

This module contains unit tests for WARC record data models.
"""

import unittest
from datetime import datetime
from typing import Dict

from models.warc_record import WarcRecord


class MockWarcRecord:
    """Mock warcio record for testing."""

    def __init__(
        self,
        rec_type: str,
        headers: Dict[str, str],
        http_headers: Dict[str, str],
        content: bytes,
    ):
        """Creates a mock WARC record.

        Args:
            rec_type: Record type.
            headers: WARC headers.
            http_headers: HTTP headers.
            content: Record content.
        """
        self.rec_type = rec_type
        self.rec_headers = MockHeaders(headers)
        self.http_headers = MockHeaders(http_headers) if http_headers else None
        self._content = content

    def content_stream(self):
        """Returns a mock content stream."""
        return MockStream(self._content)


class MockHeaders:
    """Mock headers for testing."""

    def __init__(self, headers: Dict[str, str]):
        """Creates mock headers.

        Args:
            headers: Header dictionary.
        """
        self.headers = list(headers.items())

    def get_header(self, name: str, default: str = "") -> str:
        """Gets header value by name.

        Args:
            name: Header name.
            default: Default value if header not found.

        Returns:
            Header value or default.
        """
        for header_name, value in self.headers:
            if header_name.lower() == name.lower():
                return value
        return default


class MockStream:
    """Mock content stream for testing."""

    def __init__(self, content: bytes):
        """Creates a mock stream.

        Args:
            content: Content bytes.
        """
        self._content = content

    def read(self):
        """Reads content."""
        return self._content


class TestWarcRecord(unittest.TestCase):
    """Test cases for WarcRecord class."""

    def test_from_warc_record(self):
        """Tests creation from warcio record."""
        warc_content = b"<html><body>test</body></html>"
        mock_record = MockWarcRecord(
            rec_type="response",
            headers={
                "WARC-Type": "response",
                "WARC-Record-ID": "<test-id>",
                "WARC-Target-URI": "http://example.com",
                "WARC-Date": "2025-01-24T12:34:56Z",
                "WARC-Payload-Digest": "sha1:test",
            },
            http_headers={"Content-Type": "text/html"},
            content=warc_content,
        )

        record = WarcRecord.from_warc_record(mock_record)

        self.assertEqual(record.record_type, "response")
        self.assertEqual(record.record_id, "<test-id>")
        self.assertEqual(str(record.target_uri), "http://example.com")
        self.assertIsInstance(record.date, datetime)
        self.assertEqual(str(record.content_type), "text/html")
        self.assertEqual(record.content, warc_content.decode("utf-8"))
        self.assertEqual(str(record.payload_digest), "sha1:test")

    def test_minimal_record(self):
        """Tests creation with minimal fields."""
        record = WarcRecord(
            record_id="<test-id>",
            record_type="response",
            target_uri="http://example.com",
            date=datetime(2025, 1, 24, 12, 34, 56),
            content_type="text/html",
            content="test",
            content_length=4,
            headers={},
        )

        self.assertEqual(record.record_id, "<test-id>")
        self.assertEqual(record.record_type, "response")
        self.assertEqual(str(record.target_uri), "http://example.com")
        self.assertIsInstance(record.date, datetime)
        self.assertEqual(str(record.content_type), "text/html")
        self.assertEqual(record.content, "test")
        self.assertEqual(record.content_length, 4)
        self.assertEqual(record.headers, {})
        self.assertIsNone(record.payload_digest)


if __name__ == "__main__":
    unittest.main()
