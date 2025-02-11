"""Tests for warc_processor_main module."""

import unittest
from warc_processor_main import main


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
        with self.assertRaises(SystemExit):
            main(["--config", "dummy_config.yaml"])





    def test_no_input_files_are_provided(self):
        with self.assertRaises(SystemExit):
            self.assertEqual(main([]), None)


if __name__ == "__main__":
    unittest.main()
