"""Tests for WarcProcessor."""

import io
import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from models.warc_mime_types import ContentType
from models.warc_record import WarcRecord
from warc_record_processor import ProcessorInput, WarcRecordProcessor
from warc_processor import WarcProcessor
from warc_record_parser import WarcRecordParser
from processing_stats import ProcessingStats
from output_writer import OutputWriter


class MockProcessor(WarcRecordProcessor):
    """Mock processor for testing."""

    def __init__(self, can_process_result=True, process_result="processed"):
        self._can_process_result = can_process_result
        self._process_result = process_result
        self.can_process_called = False
        self.process_called = False

    def can_process(self, content_type: ContentType) -> bool:
        """Mock can_process method."""
        if content_type is None:
            return False
        self.can_process_called = True
        return self._can_process_result

    def process(self, processor_input: ProcessorInput) -> str:
        """Mock process method."""
        self.process_called = True
        if self._process_result is None:
            raise ValueError("Processing failed")
        return self._process_result


class TestWarcProcessor(unittest.TestCase):
    """Test the WARC processor."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_path = os.path.join(self.temp_dir, "output.txt")

        self.mock_processor = MagicMock(spec=WarcRecordProcessor)
        self.mock_output_writer = MagicMock(spec=OutputWriter)
        self.mock_record_parser = MagicMock(spec=WarcRecordParser)
        self.mock_stats = MagicMock(spec=ProcessingStats)

        self.processor = WarcProcessor(
            processor=self.mock_processor,
            output_writer=self.mock_output_writer,
            record_parser=self.mock_record_parser,
            stats=self.mock_stats,
        )

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary directory
        if os.path.exists(self.temp_dir):
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            os.rmdir(self.temp_dir)

    def create_record(self, content="test content", content_type=None):
        """Create a test WARC record."""
        record = WarcRecord(
            warc_type="response",
            warc_date=datetime.now(),
            warc_record_id="test-record-id",
            content_length=len(content) if content else 0,
            content_type=content_type,
            content=content,
            target_uri="http://example.com",
            record_id="<urn:uuid:12345678>",
            record_type="response",
            date=datetime.now(),
        )
        return record

    def test_process_record_success(self):
        """Test successful record processing."""
        content_type = ContentType("text/html")
        record = self.create_record(content_type=content_type)
        processor_input = ProcessorInput(
            content=record.content, content_type=content_type
        )

        self.mock_processor.can_process = MagicMock(return_value=True)
        self.mock_processor.process = MagicMock(return_value="processed")

        # pylint: disable=protected-access
        result = self.processor._process_record(record)

        self.assertEqual(result, "processed")
        self.mock_processor.can_process.assert_called_once_with(content_type)
        self.mock_processor.process.assert_called_once_with(processor_input)

    def test_process_record_no_processor(self):
        """Test when no processor can handle the record."""
        self.mock_processor.can_process.return_value = False
        record = self.create_record(content_type="text/html")

        # pylint: disable=protected-access
        result = self.processor._process_record(record)

        self.assertIsNone(result)
        self.mock_processor.process.assert_not_called()

    def test_process_record_processing_error(self):
        """Test when processing fails."""
        self.mock_processor.process.side_effect = ValueError(
            "Processing failed"
        )
        record = self.create_record(content_type="text/html")

        # pylint: disable=protected-access
        result = self.processor._process_record(record)

        self.assertIsNone(result)

    def test_process_record_no_content(self):
        """Test processing record with no content."""
        record = self.create_record(content_type="text/html", content=None)

        # pylint: disable=protected-access
        result = self.processor._process_record(record)

        self.assertIsNone(result)
        self.mock_processor.can_process.assert_not_called()

    def test_process_record_no_content_type(self):
        """Test processing record with no content type."""
        record = self.create_record(content_type=None)

        # pylint: disable=protected-access
        result = self.processor._process_record(record)

        self.assertIsNone(result)
        self.mock_processor.can_process.assert_not_called()

    def test_process_warc_file_no_input(self):
        """Test processing with no input file."""
        with self.assertRaises(ValueError) as cm:
            self.processor.process_warc_file("", "output.txt")
        self.assertEqual(str(cm.exception), "No input file provided")

    def test_process_warc_file_no_output(self):
        """Test processing with no output file."""
        with self.assertRaises(ValueError) as cm:
            self.processor.process_warc_file("input.warc", "")
        self.assertEqual(str(cm.exception), "No output path provided")

    def test_process_warc_file_existing_output(self):
        """Test processing with existing output file and no overwrite."""
        # Create output file
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write("existing content")

        with self.assertRaises(FileExistsError) as cm:
            self.processor.process_warc_file("input.warc", self.output_path)
        self.assertEqual(
            str(cm.exception),
            f"Output file already exists: {self.output_path}. "
            "Use overwrite=True to overwrite."
        )

    @patch("builtins.open", create=True)
    def test_process_warc_file_existing_output_with_overwrite(self, mock_open):
        """Test processing with existing output file and overwrite=True."""
        # Create output file
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write("existing content")

        # Mock the file processing
        mock_file = io.BytesIO()
        mock_open.return_value.__enter__.return_value = mock_file
        self.mock_record_parser.parse.return_value = None

        # Should not raise FileExistsError
        self.processor.process_warc_file(
            "input.warc", self.output_path, overwrite=True
        )

        # Verify stats were tracked
        self.mock_stats.start_processing.assert_called_once_with("input.warc")
        self.mock_stats.finish_processing.assert_called_once()

    @patch("builtins.open", create=True)
    def test_process_warc_file(self, mock_open):
        """Test processing a WARC file."""
        # Setup mock record
        record = self.create_record()
        self.mock_record_parser.parse.return_value = record

        # Setup mock file with WARC content
        mock_file = io.BytesIO(
            b"WARC/1.0\r\n"
            b"WARC-Type: response\r\n"
            b"WARC-Date: 2023-01-01T00:00:00Z\r\n"
            b"WARC-Record-ID: <urn:uuid:12345678>\r\n"
            b"WARC-Target-URI: http://example.com\r\n"
            b"Content-Length: 12\r\n"
            b"Content-Type: text/html\r\n"
            b"\r\n"
            b"test content"
        )
        mock_open.return_value.__enter__.return_value = mock_file

        self.processor.process_warc_file("test.warc", "test.out")

        # Check that stats were tracked
        self.mock_stats.start_processing.assert_called_once_with("test.warc")
        self.mock_stats.track_parsed_record.assert_called_once()
        self.mock_stats.track_skipped_record.assert_called_once()
        self.mock_stats.finish_processing.assert_called_once()

        # Check that output writer was configured
        self.mock_output_writer.configure.assert_called_once_with("test.out")

    @patch("builtins.open", create=True)
    def test_process_warc_file_skips_failed_records(self, mock_open):
        """Test that processing continues after record failures."""
        # Setup mock records
        record1 = self.create_record()
        record2 = self.create_record()
        self.mock_record_parser.parse.side_effect = [record1, record2]

        # Setup mock file with WARC content
        mock_file = io.BytesIO(
            b"WARC/1.0\r\n"
            b"WARC-Type: response\r\n"
            b"WARC-Date: 2023-01-01T00:00:00Z\r\n"
            b"WARC-Record-ID: <urn:uuid:12345678>\r\n"
            b"WARC-Target-URI: http://example.com\r\n"
            b"Content-Length: 12\r\n"
            b"Content-Type: text/html\r\n"
            b"\r\n"
            b"test content\r\n"
            b"\r\n"
            b"WARC/1.0\r\n"
            b"WARC-Type: response\r\n"
            b"WARC-Date: 2023-01-01T00:00:00Z\r\n"
            b"WARC-Record-ID: <urn:uuid:87654321>\r\n"
            b"WARC-Target-URI: http://example.com\r\n"
            b"Content-Length: 12\r\n"
            b"Content-Type: text/html\r\n"
            b"\r\n"
            b"test content"
        )
        mock_open.return_value.__enter__.return_value = mock_file

        # Make first record fail processing
        self.mock_processor.process.side_effect = ValueError(
            "Processing failed"
        )

        self.processor.process_warc_file("test.warc", "test.out")

        # Check that stats were tracked for both records
        self.mock_stats.start_processing.assert_called_once_with("test.warc")
        self.assertEqual(self.mock_stats.track_parsed_record.call_count, 2)
        self.assertEqual(self.mock_stats.track_skipped_record.call_count, 2)
        self.mock_stats.finish_processing.assert_called_once()

        # Check that output writer was configured
        self.mock_output_writer.configure.assert_called_once_with("test.out")


if __name__ == "__main__":
    unittest.main()
