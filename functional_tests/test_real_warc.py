"""Functional tests for WARC processor."""

import os
import tempfile
from datetime import datetime
from unittest import TestCase

from html_processor import HtmlProcessor
from warc_processor_factory import WarcProcessorFactory


class TestRealWarc(TestCase):
    """Tests for processing real WARC files."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file path but don't open it yet
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            self.output_path = temp.name

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'output_path') and os.path.exists(self.output_path):
            os.unlink(self.output_path)

    def test_process_cc_news(self):
        """Tests processing a real Common Crawl News WARC file."""
        warc_path = os.path.join(os.path.dirname(__file__), "..", "tests",
                                 "fixtures", "sample_recompressed.warc.gz")

        # Skip test if WARC file doesn't exist
        if not os.path.exists(warc_path):
            self.skipTest(f"WARC file not found: {warc_path}")

        # Get input file size
        input_size = os.path.getsize(warc_path) / (1024 * 1024)  # MB
        print(f"\nInput file size: {input_size:.1f} MB")

        # Process WARC file
        start_time = datetime.now()
        processor = WarcProcessorFactory.create([HtmlProcessor()])
        stats = processor.process_warc_file(warc_path, self.output_path)
        processing_time = datetime.now() - start_time

        # Basic validation
        self.assertTrue(os.path.exists(self.output_path))

        # Print debug info
        print(f"\nOutput file path: {self.output_path}")
        print("\nOutput file contents:")
        with open(self.output_path, 'r', encoding='utf-8') as f:
            print(f.read())

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
