"""Tests for WARC record parser.

This module contains unit tests for the WARC record parser functionality.
"""

import unittest
from unittest.mock import MagicMock

from warcio.statusandheaders import StatusAndHeaders
from models.warc_mime_types import ContentType
from warc_record_parser import WarcRecordParser


class TestWarcRecordParser(unittest.TestCase):
    """Test cases for WARC record parser."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = WarcRecordParser()

        # Create mock warcio record
        self.mock_record = MagicMock()
        self.mock_record.rec_type = 'response'
        self.mock_record.rec_headers = StatusAndHeaders('WARC/1.0', [
            ('WARC-Type', 'response'),
            ('WARC-Record-ID', '<test-id>'),
            ('WARC-Target-URI', 'http://example.com'),
            ('WARC-Date', '2025-01-24T12:34:56Z'),
        ])
        self.mock_record.http_headers = StatusAndHeaders(
            '200 OK', [
                ('Content-Type', 'text/html'),
            ])
        self.mock_record.content_stream(
        ).read.return_value = b'<html><body>test</body></html>'

    def test_parse_valid_record(self):
        """Test parsing a valid WARC record."""
        record = self.parser.parse(self.mock_record)

        self.assertIsNotNone(record)
        self.assertEqual(record.record_type, 'response')
        self.assertEqual(record.record_id, '<test-id>')
        self.assertEqual(str(record.target_uri), 'http://example.com')
        self.assertEqual(record.date, '2025-01-24T12:34:56Z')
        self.assertEqual(record.content_type, ContentType('text/html'))
        self.assertEqual(record.content, '<html><body>test</body></html>')

    def test_parse_non_response_record(self):
        """Test parsing a non-response record."""
        self.mock_record.rec_type = 'request'
        record = self.parser.parse(self.mock_record)

        self.assertIsNone(record)

    def test_parse_non_200_response(self):
        """Test parsing a non-200 response."""
        self.mock_record.http_headers = StatusAndHeaders('404 Not Found', [])
        record = self.parser.parse(self.mock_record)

        self.assertIsNone(record)

    def test_parse_missing_required_fields(self):
        """Test parsing a record with missing required fields."""
        self.mock_record.rec_headers = StatusAndHeaders('WARC/1.0', [])
        record = self.parser.parse(self.mock_record)

        self.assertIsNone(record)

    def test_parse_malformed_record(self):
        """Test parsing a malformed record."""
        self.mock_record.content_stream().read.side_effect = IOError(
            'Read error')
        record = self.parser.parse(self.mock_record)

        self.assertIsNone(record)


if __name__ == '__main__':
    unittest.main()
