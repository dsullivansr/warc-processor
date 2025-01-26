"""Tests for HTML processor."""

import unittest
from datetime import datetime

from html_processor import HtmlProcessor
from models.warc_mime_types import ContentType
from models.warc_record import WarcRecord
from models.warc_identifiers import PayloadDigest, WarcRecordId, WarcUri


class TestHtmlProcessor(unittest.TestCase):
    """Test cases for HtmlProcessor class."""

    def setUp(self):
        """Sets up test fixtures."""
        self.processor = HtmlProcessor()

        # Create a test record
        self.record = WarcRecord(
            record_id=WarcRecordId('<urn:uuid:12345678>'),
            record_type='response',
            target_uri=WarcUri.from_str('http://example.com'),
            date=datetime.now(),
            content_type=ContentType('text/html'),
            content='<html><body>test</body></html>',
            content_length=25,
            headers={},
            payload_digest=PayloadDigest('sha1:1234567890'),
        )

    def test_can_process_html(self):
        """Tests that HTML content can be processed."""
        self.assertTrue(self.processor.can_process(self.record))

    def test_cannot_process_non_html(self):
        """Tests that non-HTML content is rejected."""
        self.record.content_type = ContentType('text/plain')
        self.assertFalse(self.processor.can_process(self.record))

    def test_process_simple_html(self):
        """Tests processing simple HTML content."""
        self.record.content = '<html><body>Hello World</body></html>'
        result = self.processor.process(self.record)
        self.assertEqual(result, 'Hello World')

    def test_process_with_scripts(self):
        """Tests that scripts are removed."""
        html = """
        <html>
            <head>
                <script>alert('test');</script>
            </head>
            <body>
                <p>Hello</p>
                <script>console.log('test');</script>
                <p>World</p>
            </body>
        </html>
        """
        self.record.content = html
        result = self.processor.process(self.record)
        self.assertEqual(result.strip(), 'Hello World')

    def test_process_with_styles(self):
        """Tests that styles are removed."""
        html = """
        <html>
            <head>
                <style>body { color: red; }</style>
            </head>
            <body>
                <p>Hello</p>
                <style>p { font-size: 12px; }</style>
                <p>World</p>
            </body>
        </html>
        """
        self.record.content = html
        result = self.processor.process(self.record)
        self.assertEqual(result.strip(), 'Hello World')

    def test_process_malformed_html(self):
        """Tests processing malformed HTML content."""
        self.record.content = '<p>Hello<p>World'
        result = self.processor.process(self.record)
        self.assertEqual(result.strip(), 'Hello World')


if __name__ == '__main__':
    unittest.main()
