"""Tests for WARC processor."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock

from warc_processor import WarcProcessor
from processing_stats import ProcessingStats
from output_writer import OutputWriter
from warc_record_parser import WarcRecordParser
from warc_record_processor_chain import WarcRecordProcessorChain


class TestWarcProcessor(unittest.TestCase):
    """Test cases for WarcProcessor."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary files
        self.temp_dir = tempfile.mkdtemp()
        self.warc_path = os.path.join(self.temp_dir, 'test.warc')
        self.output_path = os.path.join(self.temp_dir, 'output.txt')
        
        # Create mock components
        self.mock_processor = MagicMock()
        self.mock_writer = MagicMock(spec=OutputWriter)
        self.mock_parser = MagicMock(spec=WarcRecordParser)
        self.mock_chain = MagicMock(spec=WarcRecordProcessorChain)
        
        # Create mock stats with proper attributes
        self.mock_stats = MagicMock(spec=ProcessingStats)
        self.mock_stats.input_size_mb = 0.1
        self.mock_stats.records_processed = 0
        self.mock_stats.records_parsed = 0
        self.mock_stats.records_skipped = 0
        self.mock_stats.records_failed = 0
        self.mock_stats.bytes_processed = 0
        
        # Create processor
        self.processor = WarcProcessor(
            processors=[self.mock_processor],
            output_writer=self.mock_writer,
            record_parser=self.mock_parser,
            stats=self.mock_stats,
            processor_chain=self.mock_chain
        )
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_process_warc_file(self):
        """Test processing WARC file."""
        # Configure mock processor
        self.mock_processor.can_process.return_value = True
        self.mock_processor.process.return_value = 'processed content'
        
        # Configure mock chain
        self.mock_chain.process.return_value = 'processed content'
        
        # Configure mock parser
        self.mock_parser.parse.return_value = MagicMock()
        
        # Create test WARC file
        warc_content = (
            b'WARC/1.0\r\n'
            b'WARC-Type: response\r\n'
            b'WARC-Date: 2025-01-24T12:34:56Z\r\n'
            b'WARC-Record-ID: <urn:uuid:test-id>\r\n'
            b'Content-Length: 100\r\n'
            b'Content-Type: text/html\r\n'
            b'WARC-Target-URI: http://example.com\r\n'
            b'\r\n'
            b'HTTP/1.1 200 OK\r\n'
            b'Content-Type: text/html\r\n'
            b'Content-Length: 100\r\n'
            b'\r\n'
            b'test content'
        )
        
        with open(self.warc_path, 'wb') as f:
            f.write(warc_content)
            
        # Process file
        stats = self.processor.process_warc_file(self.warc_path, self.output_path)
        
        # Verify writer was configured
        self.mock_writer.configure.assert_called_once_with(self.output_path)
        
        # Verify record was written
        self.assertEqual(self.mock_writer.write_record.call_count, 1)
        
        # Verify stats
        self.assertEqual(stats.records_processed, self.mock_stats.records_processed)
        self.assertEqual(stats.records_skipped, self.mock_stats.records_skipped)
        self.assertEqual(stats.records_failed, self.mock_stats.records_failed)
        
    def test_process_warc_file_bad_output(self):
        """Test processing WARC file with bad output path."""
        # Create test WARC file
        with open(self.warc_path, 'wb') as f:
            f.write(b'test content')
            
        # Configure mock writer to raise error
        self.mock_writer.configure.side_effect = PermissionError("Permission denied")
        
        # Process file should raise error
        with self.assertRaises(PermissionError):
            self.processor.process_warc_file(self.warc_path, '/bad/path')
            
    def test_process_warc_file_missing(self):
        """Test processing missing WARC file."""
        with self.assertRaises(FileNotFoundError):
            self.processor.process_warc_file('/missing/file', self.output_path)
            
    def test_process_warc_file_no_processor(self):
        """Test processing WARC file with no matching processor."""
        # Configure mock processor
        self.mock_processor.can_process.return_value = False
        
        # Configure mock chain
        self.mock_chain.process.return_value = None
        
        # Configure mock parser
        self.mock_parser.parse.return_value = MagicMock()
        
        # Create test WARC file with valid WARC content
        warc_content = (
            b'WARC/1.0\r\n'
            b'WARC-Type: response\r\n'
            b'WARC-Date: 2025-01-24T12:34:56Z\r\n'
            b'WARC-Record-ID: <urn:uuid:test-id>\r\n'
            b'Content-Length: 100\r\n'
            b'Content-Type: text/html\r\n'
            b'WARC-Target-URI: http://example.com\r\n'
            b'\r\n'
            b'HTTP/1.1 200 OK\r\n'
            b'Content-Type: text/html\r\n'
            b'Content-Length: 100\r\n'
            b'\r\n'
            b'test content'
        )
        
        with open(self.warc_path, 'wb') as f:
            f.write(warc_content)
            
        # Process file
        stats = self.processor.process_warc_file(self.warc_path, self.output_path)
        
        # Verify no records were written
        self.mock_writer.write_record.assert_not_called()
        
        # Verify stats
        self.assertEqual(stats.records_processed, self.mock_stats.records_processed)
        self.assertEqual(stats.records_skipped, self.mock_stats.records_skipped)
        self.assertEqual(stats.records_failed, self.mock_stats.records_failed)
