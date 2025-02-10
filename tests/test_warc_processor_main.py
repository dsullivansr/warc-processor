"""Tests for warc_processor_main module."""

import os
import sys
import tempfile
import unittest
from warc_processor_main import main

import warc_processor_main


class TestWarcProcessorMain(unittest.TestCase):

    def setUp(self):
        """Set up test case."""
        self.test_file = "test_warc_processor.warc"
        self.test_content = (
            b"WARC/1.0\r\n"
            b"WARC-Type: warcinfo\r\n"
            b"WARC-Record-ID: <urn:uuid:61f1af43>\r\n"
            b"Content-Type: application/warc-fields\r\n"
            b"Content-Length: 18\r\n\r\n"
            b"version: 1.0\r\n\r\n"
        )
        # Create a minimal valid WARC file for testing purposes
        with open(self.test_file, "wb") as f:
            f.write(self.test_content)

    def test_warc_processor_exits_when_no_input_files_are_provided(self):
        with self.assertRaises(SystemExit) as cm:
            main([])
        self.assertEqual(cm.exception.code, 1)

    def test_warc_processor_runs_with_input_files(self):
        self.assertEqual(main([self.test_file]), 0)

    def test_warc_processor_module_can_be_imported_when_added_to_path(self):
        """Test that the warc_processor_main module can be imported when added
        to path."""
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        # Add the temporary directory to sys.path so that we can import the
        # warc_processor_main module
        sys.path.insert(0, temp_dir)
        # Create a dummy warc_processor_main module
        with open(
            os.path.join(temp_dir, "warc_processor_main.py"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(
                """def main():
    print('Hello, world!')"""
            )

        # Call the main function and verify it doesn't raise an exception
        try:
            warc_processor_main.main()  # Ensure this call is meaningful
        except (SystemExit, ImportError) as e:  # Specify exceptions
            self.fail(f"main() raised an unexpected exception: {e}")

    def test_no_input_files_are_provided(self):
        with self.assertRaises(SystemExit):
            self.assertEqual(main([]), None)


if __name__ == "__main__":
    unittest.main()
