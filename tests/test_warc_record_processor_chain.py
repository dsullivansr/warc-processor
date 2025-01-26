"""Tests for WARC record processor chain."""

import unittest
from unittest.mock import MagicMock

from bs4.builder import ParserRejectedMarkup
from models.warc_record import WarcRecord
from warc_record_processor import WarcRecordProcessor
from warc_record_processor_chain import WarcRecordProcessorChain


class TestWarcRecordProcessorChain(unittest.TestCase):
    """Test WarcRecordProcessorChain."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock processor
        self.mock_processor = MagicMock(spec=WarcRecordProcessor)

        # Create chain with mock processor
        self.chain = WarcRecordProcessorChain([self.mock_processor])

        # Create test record
        warc_content = (b'WARC/1.0\r\n'
                        b'WARC-Type: response\r\n'
                        b'WARC-Date: 2025-01-24T12:34:56Z\r\n'
                        b'WARC-Record-ID: <urn:uuid:test-id>\r\n'
                        b'Content-Length: 100\r\n'
                        b'Content-Type: text/html\r\n'
                        b'WARC-Target-URI: http://example.com\r\n'
                        b'\r\n')

        self.record = WarcRecord(record_id='test-id',
                                 record_type='response',
                                 target_uri='http://example.com',
                                 date='2025-01-24T12:34:56Z',
                                 content_type='text/html',
                                 content=warc_content,
                                 content_length=100,
                                 headers={})

    def test_process_html_record(self):
        """Test processing HTML record."""
        # Configure mock
        self.mock_processor.can_process.return_value = True
        self.mock_processor.process.return_value = 'test output'

        # Process record
        result = self.chain.process(self.record)

        # Verify result
        self.assertEqual(result, 'test output')
        self.mock_processor.can_process.assert_called_once_with(self.record)
        self.mock_processor.process.assert_called_once_with(self.record)

    def test_process_non_html_record(self):
        """Test processing non-HTML record."""
        # Configure mock
        self.mock_processor.can_process.return_value = False

        # Process record
        result = self.chain.process(self.record)

        # Verify result
        self.assertIsNone(result)
        self.mock_processor.can_process.assert_called_once_with(self.record)
        self.mock_processor.process.assert_not_called()

    def test_process_processor_error(self):
        """Test handling processor error."""
        # Configure mock
        self.mock_processor.can_process.return_value = True
        self.mock_processor.process.side_effect = ParserRejectedMarkup(
            'test error')

        # Process record
        result = self.chain.process(self.record)

        # Verify result
        self.assertIsNone(result)
        self.mock_processor.can_process.assert_called_once_with(self.record)
        self.mock_processor.process.assert_called_once_with(self.record)

    def test_process_no_matching_processor(self):
        """Test processing with no matching processor."""
        # Configure mock
        self.mock_processor.can_process.return_value = False

        # Process record
        result = self.chain.process(self.record)

        # Verify result
        self.assertIsNone(result)
        self.mock_processor.can_process.assert_called_once_with(self.record)
        self.mock_processor.process.assert_not_called()

    def test_multiple_processors(self):
        """Test chaining multiple processors."""
        # Create second mock processor
        mock_processor2 = MagicMock(spec=WarcRecordProcessor)

        # Create chain with both processors
        chain = WarcRecordProcessorChain([self.mock_processor, mock_processor2])

        # Configure mocks
        self.mock_processor.can_process.return_value = True
        self.mock_processor.process.return_value = 'intermediate output'
        mock_processor2.can_process.return_value = True
        mock_processor2.process.return_value = 'final output'

        # Process record
        result = chain.process(self.record)

        # Verify result
        self.assertEqual(result, 'final output')
        self.mock_processor.can_process.assert_called_once_with(self.record)
        self.mock_processor.process.assert_called_once_with(self.record)
        mock_processor2.can_process.assert_called_once_with(self.record)
        mock_processor2.process.assert_called_once_with(self.record)


if __name__ == '__main__':
    unittest.main()
