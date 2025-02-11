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

    def test_main_requires_input_argument(self):
        """Test that main requires the --input argument."""
        with self.assertRaises(SystemExit):
            main([])

    def test_main_processes_input_file(self):
        """Test that main processes the input file successfully."""
        mock_processor = unittest.mock.MagicMock()

        with unittest.mock.patch(
            'warc_processor_factory.WarcProcessor', return_value=mock_processor
        ):
            # Run the main function
            result = main(['--input', self.test_file])

            # Verify the results
            self.assertEqual(result, 0)
            mock_processor.process_warc_file.assert_called_once_with(
                self.test_file, self.test_file + '.txt'
            )

    def test_main_handles_processing_error(self):
        """Test that main handles processing errors correctly."""
        mock_processor = unittest.mock.MagicMock()
        mock_processor.process_warc_file.side_effect = RuntimeError(
            "Test error"
        )

        with unittest.mock.patch(
            'warc_processor_factory.WarcProcessor', return_value=mock_processor
        ):
            # Run the main function
            result = main(['--input', self.test_file])

            # Verify the results
            self.assertEqual(result, 1)
            mock_processor.process_warc_file.assert_called_once_with(
                self.test_file, self.test_file + '.txt'
            )


if __name__ == "__main__":
    unittest.main()
