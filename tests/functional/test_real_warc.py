"""Functional tests using real WARC files."""

import json
import os
import subprocess
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

        # Create temporary output file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            output_path = temp_file.name

        try:
            # Process WARC file using existing method
            start_time = datetime.now()
            factory = WarcProcessorFactory()
            processor = factory.create()
            processor.process_warc_file(warc_path, output_path, overwrite=True)

            # Calculate processing time
            duration = (datetime.now() - start_time).total_seconds()
            print(f"Processing time: {duration:.1f} seconds")

            # Verify output was created
            self.assertTrue(os.path.exists(output_path))
            self.assertGreater(os.path.getsize(output_path), 0)

        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    # pylint: disable=too-many-locals,line-too-long
    def test_command_line_formats(self):
        """Test processing WARC file with different output formats via command line."""
        # Get path to sample WARC file
        test_dir = os.path.dirname(__file__)
        warc_path = os.path.join(test_dir, "test_data", "sample.warc.gz")

        # Skip test if WARC file doesn't exist
        if not os.path.exists(warc_path):
            self.skipTest(f"WARC file not found: {warc_path}")

        # Test both text and JSON output formats
        formats = ['text', 'json']
        for output_format in formats:
            # Create temp output file
            suffix = f'.{output_format}'
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            ) as temp_file:
                output_path = temp_file.name

            try:
                # Build command and environment
                project_root = os.path.dirname(
                    os.path.dirname(os.path.dirname(__file__))
                )
                env = os.environ.copy()
                env['PYTHONPATH'] = project_root

                # Prepare command
                cmd = [
                    'python3', '-m', 'warc_processor_main',
                    '--input', warc_path,
                    '--output', output_path,
                    '--format', output_format,
                    '--overwrite'
                ]

                # Run command
                result = subprocess.run(
                    ' '.join(cmd),
                    env=env,
                    shell=True,
                    check=False
                ).returncode
                self.assertEqual(
                    result, 0,
                    f"Command failed with exit code {result}"
                )

                # Verify output exists and has content
                self.assertTrue(os.path.exists(output_path))
                self.assertGreater(os.path.getsize(output_path), 0)

                # Verify content format
                with open(output_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if output_format == 'json':
                        # Verify JSON structure
                        records = json.loads(content)
                        self.assertIsInstance(records, list)
                        self.assertGreater(len(records), 0)

                        # Check required fields
                        required_fields = [
                            'warc_type', 'record_id', 'date',
                            'target_uri', 'content_type',
                            'content', 'headers'
                        ]
                        for field in required_fields:
                            self.assertIn(field, records[0])
                    else:
                        # Verify WARC format
                        self.assertIn('WARC/1.0', content)
                        self.assertIn('WARC-Type:', content)
                        self.assertIn('WARC-Target-URI:', content)
                        self.assertIn('WARC-Date:', content)

            finally:
                # Clean up
                if os.path.exists(output_path):
                    os.unlink(output_path)
