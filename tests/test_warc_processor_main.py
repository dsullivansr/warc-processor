"""Tests for warc_processor_main module."""

import os
import tempfile
import unittest
from unittest.mock import patch

from warc_processor_main import main


class TestWarcProcessorMain(unittest.TestCase):
    """Test cases for warc_processor_main module."""

    def setUp(self):
        """Set up test case."""
        tmp_dir = tempfile.gettempdir()
        self.input_file = os.path.join(tmp_dir, 'test.warc')
        self.output_file = os.path.join(tmp_dir, 'test.txt')
        self.config_file = os.path.join(tmp_dir, 'test_config.yaml')

        # Create empty input file
        with open(self.input_file, 'w', encoding='utf-8') as f:
            f.write('')

        # Create test config
        with open(self.config_file, 'w', encoding='utf-8') as f:
            f.write('''
processors:
  - class: BeautifulSoupHtmlProcessor
    config:
      parser: html5lib
''')

    def tearDown(self):
        """Clean up test case."""
        for file in [self.input_file, self.output_file, self.config_file]:
            if os.path.exists(file):
                os.remove(file)

    def test_main_with_valid_file(self):
        """Test main with valid WARC file."""
        with patch('sys.argv', [
                'warc_processor_main.py',
                self.input_file,
                '--output',
                self.output_file,
                '--config',
                self.config_file,
        ]):
            with patch('warc_processor_factory.WarcProcessorFactory.'
                       'create_from_config') as mock_create:
                exit_code = main()
                self.assertEqual(exit_code, 0)
                mock_create.assert_called_once()

    def test_main_with_parser_option(self):
        """Test main with parser option."""
        args = [
            'warc_processor_main.py',
            self.input_file,
            '--output',
            self.output_file,
            '--parser',
            'html.parser',
            '--config',
            self.config_file,
        ]
        with patch('sys.argv', args):
            with patch('warc_processor_factory.WarcProcessorFactory.'
                       'create_from_config') as mock_create:
                exit_code = main()
                self.assertEqual(exit_code, 0)
                mock_create.assert_called_once_with(self.config_file,
                                                    parser='html.parser')

    def test_main_with_invalid_file(self):
        """Test main with invalid WARC file."""
        with patch('sys.argv', [
                'warc_processor_main.py',
                'nonexistent.warc',
                '--output',
                self.output_file,
                '--config',
                self.config_file,
        ]):
            exit_code = main()
            self.assertEqual(exit_code, 1)


if __name__ == '__main__':
    unittest.main()
