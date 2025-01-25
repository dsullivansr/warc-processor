"""Test cases for ProcessedWarcRecord."""

import unittest
from models.warc_record import WarcRecord, ProcessedWarcRecord


class TestProcessedWarcRecord(unittest.TestCase):
    """Test cases for ProcessedWarcRecord."""
    
    def setUp(self):
        """Set up test case."""
        self.warc_record = WarcRecord(
            record_type='response',
            target_uri='https://example.com',
            date='2020-01-01T00:00:00Z',
            content_type='text/html',
            payload_digest='sha1:1234',
            record_id='<urn:uuid:1234>',
            content='<html><body>Test content</body></html>',
            content_length=100,
            headers={'Content-Type': 'text/html'}
        )
        self.processed_content = 'Processed test content'
        self.metadata = {'key': 'value'}
        
    def test_from_warc_record(self):
        """Test creating ProcessedWarcRecord from WarcRecord."""
        record = ProcessedWarcRecord.from_record(
            self.warc_record,
            processed_content=self.processed_content,
            metadata=self.metadata
        )
        
        self.assertEqual(record.url, self.warc_record.target_uri)
        self.assertEqual(record.processed_content, self.processed_content)
        self.assertEqual(record.metadata, self.metadata)
        self.assertEqual(record.original_record, self.warc_record)
        
    def test_from_warc_record_no_metadata(self):
        """Test creating ProcessedWarcRecord without metadata."""
        record = ProcessedWarcRecord.from_record(
            self.warc_record,
            processed_content=self.processed_content
        )
        
        self.assertEqual(record.metadata, {})
        
    def test_str_representation(self):
        """Test string representation of ProcessedWarcRecord."""
        record = ProcessedWarcRecord.from_record(
            self.warc_record,
            processed_content=self.processed_content,
            metadata=self.metadata
        )
        
        str_repr = str(record)
        self.assertIn(self.warc_record.target_uri, str_repr)
        self.assertIn(str(len(self.processed_content)), str_repr)
