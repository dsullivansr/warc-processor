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
        self.output_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        
    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.output_file.name)
        
    def test_process_cc_news(self):
        """Tests processing a real Common Crawl News WARC file."""
        warc_path = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "sample_recompressed.warc.gz")
        
        # Skip test if WARC file doesn't exist
        if not os.path.exists(warc_path):
            self.skipTest(f"WARC file not found: {warc_path}")
            
        # Get input file size
        input_size = os.path.getsize(warc_path) / (1024 * 1024)  # MB
        print(f"\nInput file size: {input_size:.1f} MB")
        
        # Process WARC file
        start_time = datetime.now()
        processor = WarcProcessorFactory.create([HtmlProcessor()])
        stats = processor.process_warc_file(warc_path, self.output_file.name)
        processing_time = datetime.now() - start_time
        
        # Basic validation
        self.assertTrue(os.path.exists(self.output_file.name))
        
        # Print debug info
        print(f"\nOutput file path: {self.output_file.name}")
        print("\nOutput file contents:")
        with open(self.output_file.name, 'r', encoding='utf-8') as f:
            print(f.read())
            
        # Validate stats - File contains:
        # - 6 response records (6 HTML, 0 non-HTML)
        # - 4 request records (not counted in stats)
        # All HTML responses should be processed, including duplicates
        self.assertEqual(stats.records_parsed, 6, "Should parse 6 response records")
        self.assertEqual(stats.records_processed, 6, "All HTML responses should be processed")
        self.assertEqual(stats.records_skipped, 0, "No records should be skipped")
        self.assertEqual(stats.records_failed, 0, "No records should fail")
        
        # Print performance info
        print(f"\nProcessing time: {processing_time.total_seconds():.2f}s")
