"""Functional tests using real WARC files."""

import os
import tempfile
from datetime import datetime
from unittest import TestCase

from beautiful_soup_html_processor import BeautifulSoupHtmlProcessor
from plain_text_writer import PlainTextWriter
from warc_processor_factory import WarcProcessorFactory


class TestRealWarc(TestCase):
    """Test processing real WARC files."""

    def setUp(self):
        """Set up test cases."""
        # Create a temporary file path but don't open it yet
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            self.output_path = temp.name

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'output_path') and os.path.exists(self.output_path):
            os.unlink(self.output_path)

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

        # Process WARC file
        start_time = datetime.now()
        output_writer = PlainTextWriter()
        processor = WarcProcessorFactory.create([BeautifulSoupHtmlProcessor()],
                                                output_writer=output_writer)
        stats = processor.process_warc_file(warc_path, self.output_path)
        processing_time = datetime.now() - start_time

        # Basic validation
        self.assertTrue(os.path.exists(self.output_path))

        # Verify WARC format in output
        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Basic WARC format checks
            self.assertTrue(content.startswith('WARC/1.0\n'))
            self.assertTrue('WARC/1.0' in content)

            # Required WARC headers should be present
            self.assertIn('WARC-Type:', content)
            self.assertIn('WARC-Record-ID:', content)
            self.assertIn('WARC-Date:', content)
            self.assertIn('WARC-Target-URI:', content)
            self.assertIn('Content-Type:', content)

            # Should have blank line between headers and content
            self.assertIn('\n\n', content)

            # Content should be plaintext (no HTML tags)
            self.assertNotIn('<html', content.lower())
            self.assertNotIn('<body', content.lower())
            self.assertNotIn('</html>', content.lower())

            print("\nOutput file contents:")
            print(content)

        # Validate stats
        self.assertGreater(stats.records_parsed, 0)
        self.assertGreater(stats.records_processed, 0)
        self.assertGreaterEqual(stats.records_skipped, 0)
        self.assertGreater(stats.bytes_processed, 0)

        # Print performance stats
        print(
            f"\nProcessing time: {processing_time.total_seconds():.1f} seconds")
        print(f"Records parsed: {stats.records_parsed}")
        print(f"Records processed: {stats.records_processed}")
        print(f"Records skipped: {stats.records_skipped}")
        print(f"Bytes processed: {stats.bytes_processed:,}")
        throughput = input_size / processing_time.total_seconds()
        print(f"Throughput: {throughput:.1f} MB/s")
