"""Tests for the WarcProcessorMain module."""

import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from warc_processor_main import main


class TestWarcProcessorMain(unittest.TestCase):
    """Test cases for WarcProcessorMain."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.warc_path = os.path.join(self.temp_dir, 'test.warc')
        self.output_path = os.path.join(self.temp_dir, 'output.txt')

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def create_test_warc(self):
        """Create a test WARC file."""
        warc_content = (b'WARC/1.0\r\n'
                        b'WARC-Type: response\r\n'
                        b'WARC-Date: 2025-01-24T12:34:56Z\r\n'
                        b'WARC-Record-ID: <urn:uuid:test-id>\r\n'
                        b'Content-Length: 100\r\n'
                        b'Content-Type: text/html\r\n'
                        b'WARC-Target-URI: http://example.com\r\n'
                        b'\r\n'
                        b'test content')

        with open(self.warc_path, 'wb') as f:
            f.write(warc_content)

    def test_main_no_args(self):
        """Tests main with no arguments."""
        with patch('sys.argv', ['warc_processor_main.py']):
            with self.assertRaises(SystemExit):
                main()

    def test_main_with_args(self):
        """Tests main with valid arguments."""
        self.create_test_warc()

        mock_html_processor = MagicMock()
        mock_html_processor.can_process.return_value = True
        mock_html_processor.process.return_value = 'processed content'

        with patch(
                'sys.argv',
            ['warc_processor_main.py', self.warc_path, self.output_path]):
            with patch('html_processor.HtmlProcessor',
                       return_value=mock_html_processor):
                main()

        self.assertTrue(os.path.exists(self.output_path))


if __name__ == '__main__':
    unittest.main()
