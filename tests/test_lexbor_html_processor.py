"""Tests for Lexbor HTML processor."""

import unittest
from datetime import datetime

from lexbor_html_processor import LexborHtmlProcessor
from models.warc_mime_types import ContentType
from models.warc_record import WarcRecord
from models.warc_identifiers import PayloadDigest, WarcRecordId, WarcUri


class TestLexborHtmlProcessor(unittest.TestCase):
    """Test cases for LexborHtmlProcessor class."""

    def setUp(self):
        """Sets up test fixtures."""
        self.processor = LexborHtmlProcessor()

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

    def test_process_empty_content(self):
        """Tests processing empty content."""
        self.record.content = ''
        result = self.processor.process(self.record)
        self.assertIsNone(result)

    def test_process_none_content(self):
        """Tests processing None content."""
        self.record.content = None
        result = self.processor.process(self.record)
        self.assertIsNone(result)

    def test_process_non_html_content(self):
        """Tests processing non-HTML content."""
        self.record.content = 'Hello World'
        result = self.processor.process(self.record)
        self.assertEqual(result, 'Hello World')

    def test_process_complex_html(self):
        """Tests processing complex HTML with nested elements."""
        html = """
        <html>
            <body>
                <div class="container">
                    <article>
                        <h1>Title</h1>
                        <p>First paragraph</p>
                        <div class="nested">
                            <p>Nested content</p>
                        </div>
                    </article>
                    <footer>Footer text</footer>
                </div>
            </body>
        </html>
        """
        self.record.content = html
        result = self.processor.process(self.record)
        expected = 'Title First paragraph Nested content Footer text'
        self.assertEqual(result.strip(), expected)


if __name__ == '__main__':
    unittest.main()
