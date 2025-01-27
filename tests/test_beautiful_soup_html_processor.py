"""Tests for BeautifulSoupHtmlProcessor."""

import unittest
from datetime import datetime
from unittest.mock import patch

from beautiful_soup_html_processor import BeautifulSoupHtmlProcessor
from models.warc_record import WarcRecord


class TestBeautifulSoupHtmlProcessor(unittest.TestCase):
    """Test cases for BeautifulSoupHtmlProcessor class."""

    def setUp(self):
        """Set up test cases."""
        self.processor = BeautifulSoupHtmlProcessor()

    def create_record(self, content_type='text/html', content=''):
        """Create a test record."""
        return WarcRecord(record_id='<urn:uuid:12345678>',
                          record_type='response',
                          target_uri='http://example.com',
                          date=datetime.now(),
                          content_type=content_type,
                          content=content)

    def test_can_process_html(self):
        """Test can_process with HTML content."""
        record = self.create_record(content_type='text/html')
        self.assertTrue(self.processor.can_process(record))

    def test_can_process_xhtml(self):
        """Test can_process with XHTML content."""
        record = self.create_record(content_type='application/xhtml+xml')
        self.assertTrue(self.processor.can_process(record))

    def test_cannot_process_non_html(self):
        """Test can_process with non-HTML content."""
        record = self.create_record(content_type='text/plain')
        self.assertFalse(self.processor.can_process(record))

    def test_process_html(self):
        """Test processing HTML content."""
        html = '<html><body><p>Hello world!</p></body></html>'
        record = self.create_record(content=html)
        result = self.processor.process(record)
        self.assertEqual(result, 'Hello world!')

    def test_process_html_with_scripts(self):
        """Test processing HTML with script tags."""
        html = '''
            <html>
                <head>
                    <script>alert('test');</script>
                </head>
                <body>
                    <p>Hello world!</p>
                </body>
            </html>
        '''
        record = self.create_record(content=html)
        result = self.processor.process(record)
        self.assertEqual(result, 'Hello world!')

    def test_process_html_with_styles(self):
        """Test processing HTML with style tags."""
        html = '''
            <html>
                <head>
                    <style>p { color: red; }</style>
                </head>
                <body>
                    <p>Hello world!</p>
                </body>
            </html>
        '''
        record = self.create_record(content=html)
        result = self.processor.process(record)
        self.assertEqual(result, 'Hello world!')

    def test_process_invalid_html(self):
        """Test processing invalid HTML raises error."""
        record = self.create_record(content='invalid')
        with patch('bs4.BeautifulSoup') as mock_soup:
            mock_soup.side_effect = Exception('Parse error')
            with self.assertRaises(ValueError):
                self.processor.process(record)


if __name__ == '__main__':
    unittest.main()
