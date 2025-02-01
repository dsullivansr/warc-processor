"""Tests for WARC processor main script."""

import os
import tempfile
import unittest
from unittest.mock import patch

from processors.beautiful_soup_html_processor import BeautifulSoupHtmlProcessor
from warc_processor_main import main


class TestWarcProcessorMain(unittest.TestCase):
    """Test cases for WARC processor main script."""

    def setUp(self):
        """Set up test cases."""
        # Create temporary files
        self.input_file = tempfile.mktemp()
        self.output_file = tempfile.mktemp()

        # Create a test WARC file
        with open(self.input_file, 'w', encoding='utf-8') as f:
            f.write('WARC/1.0\r\n')
            f.write('WARC-Type: response\r\n')
            f.write('WARC-Record-ID: <urn:uuid:12345678>\r\n')
            f.write('WARC-Date: 2025-01-27T01:00:45Z\r\n')
            f.write('WARC-Target-URI: http://example.com\r\n')
            f.write('Content-Length: 200\r\n')
            f.write('\r\n')
            f.write('HTTP/1.1 200 OK\r\n')
            f.write('Content-Type: text/html\r\n')
            f.write('Content-Length: 31\r\n')
            f.write('\r\n')
            f.write('<html><body>test</body></html>\r\n')

    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary files
        for path in [self.input_file, self.output_file]:
            if os.path.exists(path):
                os.remove(path)

    def test_main_with_valid_file(self):
        """Test main with valid WARC file."""
        with patch('sys.argv', [
                'warc_processor_main.py', self.input_file, '--output',
                self.output_file
        ]):
            exit_code = main()
            self.assertEqual(exit_code, 0)
            self.assertTrue(os.path.exists(self.output_file))
            self.assertGreater(os.path.getsize(self.output_file), 0)

    def test_main_with_invalid_file(self):
        """Test main with invalid WARC file."""
        with patch('sys.argv', [
                'warc_processor_main.py', 'nonexistent.warc', '--output',
                self.output_file
        ]):
            exit_code = main()
            self.assertEqual(exit_code, 1)

    def test_main_with_parser_option(self):
        """Test main with parser option."""
        args = [
            'warc_processor_main.py', self.input_file, '--output',
            self.output_file, '--parser', 'html.parser'
        ]
        with patch('sys.argv', args):
            with patch('warc_processor_factory.WarcProcessorFactory.create'
                      ) as mock_create:
                exit_code = main()
                self.assertEqual(exit_code, 0)
                mock_create.assert_called_once()
                processor = mock_create.call_args[0][0][0]
                self.assertIsInstance(processor, BeautifulSoupHtmlProcessor)
                self.assertEqual(processor.parser, 'html.parser')


if __name__ == '__main__':
    unittest.main()
