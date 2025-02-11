"""Functional tests using real WARC files."""

import os
import tempfile
import unittest
from datetime import datetime

from warc_processor_factory import WarcProcessorFactory


class TestRealWarc(unittest.TestCase):
    """Test cases using real WARC files."""


    def test_process_sample_warc(self):
        """Tests processing a sample WARC file with plaintext output."""
        warc_path = os.path.join(
            os.path.dirname(__file__), "test_data", "sample.warc.gz"
        )

        # Skip test if WARC file doesn't exist
        if not os.path.exists(warc_path):
            self.skipTest(f"WARC file not found: {warc_path}")

        # Get input file size
        input_size = os.path.getsize(warc_path) / (1024 * 1024)  # MB
        print(f"\nInput file size: {input_size:.1f} MB")

        print("\nTesting with configured processors:")

        # Create temporary output file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            output_path = temp_file.name

        try:
            # Process WARC file using existing method
            start_time = datetime.now()
            factory = WarcProcessorFactory()
            processor = factory.create(processor_type="BeautifulSoupHtmlProcessor")
            processor.process_warc_file(warc_path, output_path)

            # Calculate processing time
            duration = (datetime.now() - start_time).total_seconds()
            print(f"Processing time: {duration:.1f} seconds")

            # Verify output was created
            self.assertTrue(os.path.exists(output_path))
            self.assertGreater(os.path.getsize(output_path), 0)

        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
