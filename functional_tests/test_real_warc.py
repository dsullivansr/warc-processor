"""Test processing real WARC files."""

import os
from datetime import datetime
from unittest import TestCase

from beautiful_soup_html_processor import BeautifulSoupHtmlProcessor
from lexbor_html_processor import LexborHtmlProcessor
from plain_text_writer import PlainTextWriter
from warc_processor_factory import WarcProcessorFactory


class TestRealWarc(TestCase):
    """Test processing real WARC files."""

    def setUp(self):
        """Set up test fixtures."""
        self.output_path = os.path.join(os.path.dirname(__file__), "..",
                                        "test_data", "output.warc")

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

    def _validate_warc_content(self, content: str):
        """Validate WARC file content.

        Args:
            content: WARC file content to validate
        """
        # Basic WARC format checks
        self.assertTrue(content.startswith('WARC/1.0\n'),
                        "WARC file should start with WARC/1.0")

        # Required WARC headers
        required_headers = [
            'WARC-Type:', 'WARC-Record-ID:', 'WARC-Date:', 'WARC-Target-URI:',
            'Content-Type:'
        ]
        for header in required_headers:
            self.assertIn(header, content,
                          f"WARC file missing required header: {header}")

        # Should have blank line between headers and content
        self.assertIn(
            '\n\n', content,
            "WARC file should have blank line between headers/content")

        # Content should be plaintext (no HTML tags)
        html_tags = ['<html', '<body', '</html>']
        for tag in html_tags:
            self.assertNotIn(tag, content.lower(),
                             f"WARC file should not contain HTML tag: {tag}")

    def test_process_sample_warc(self):
        """Tests processing a sample WARC file with plaintext output."""
        warc_path = os.path.join(os.path.dirname(__file__), "..", "test_data",
                                 "sample.warc.gz")

        # Skip test if WARC file doesn't exist
        if not os.path.exists(warc_path):
            self.skipTest(f"WARC file not found: {warc_path}")

        # Get input file size
        input_size = os.path.getsize(warc_path) / (1024 * 1024)  # MB
        print(f"\nInput file size: {input_size:.1f} MB")

        # Test with both HTML processors
        processors = [
            ('BeautifulSoup', BeautifulSoupHtmlProcessor()),
            ('Lexbor', LexborHtmlProcessor()),
        ]

        for name, html_processor in processors:
            with self.subTest(processor=name):
                print(f"\nTesting with {name} processor:")

                # Process WARC file
                start_time = datetime.now()
                output_writer = PlainTextWriter()
                processor = WarcProcessorFactory.create(
                    [html_processor], output_writer=output_writer)
                stats = processor.process_warc_file(warc_path, self.output_path)
                processing_time = datetime.now() - start_time

                # Basic validation
                self.assertTrue(os.path.exists(self.output_path))

                # Verify WARC format in output
                with open(self.output_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self._validate_warc_content(content)
                    print("\nOutput file contents:")
                    print(content)

                # Validate stats
                self.assertGreater(stats.records_parsed, 0,
                                   "Should parse at least one record")
                self.assertGreater(stats.records_processed, 0,
                                   "Should process at least one record")
                self.assertGreaterEqual(
                    stats.records_skipped, 0,
                    "Should not have negative skipped records")
                self.assertGreater(stats.bytes_processed, 0,
                                   "Should process some bytes")

                # Print performance stats
                print(
                    f"\nProcessing time: {processing_time.total_seconds():.1f} "
                    f"seconds")
                print(f"Records parsed: {stats.records_parsed}")
                print(f"Records processed: {stats.records_processed}")
                print(f"Records skipped: {stats.records_skipped}")
                print(f"Bytes processed: {stats.bytes_processed:,}")
                throughput = input_size / processing_time.total_seconds()
                print(f"Throughput: {throughput:.1f} MB/s")
