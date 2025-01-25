"""Tests for WARC record models.

This module contains unit tests for WARC record data models.
"""

import unittest
from datetime import datetime
from unittest import TestCase
from typing import Dict

from models.warc_mime_types import ContentType
from models.warc_identifiers import PayloadDigest, WarcRecordId, WarcUri
from models.warc_record import WarcRecord


class MockWarcRecord:
    """Mock warcio record for testing."""
    
    def __init__(self, rec_type: str, headers: Dict[str, str], 
                 http_headers: Dict[str, str], content: bytes):
        """Creates a mock WARC record.
        
        Args:
            rec_type: Record type.
            headers: WARC headers.
            http_headers: HTTP headers.
            content: Record content.
        """
        self.rec_type = rec_type
        self.rec_headers = MockHeaders(headers)
        self.http_headers = MockHeaders(http_headers) if http_headers else None
        self._content = content
        
    def content_stream(self):
        """Returns a mock content stream."""
        return MockStream(self._content)


class MockHeaders:
    """Mock headers for testing."""
    
    def __init__(self, headers: Dict[str, str]):
        """Creates mock headers.
        
        Args:
            headers: Header dictionary.
        """
        self.headers = list(headers.items())

    def get_header(self, name: str, default: str = '') -> str:
        """Gets header value by name.
        
        Args:
            name: Header name.
            default: Default value if header not found.
            
        Returns:
            Header value or default.
        """
        for key, value in self.headers:
            if key.lower() == name.lower():
                return value
        return default


class MockStream:
    """Mock content stream for testing."""
    
    def __init__(self, content: bytes):
        """Creates a mock stream.
        
        Args:
            content: Content bytes.
        """
        self._content = content
        
    def read(self) -> bytes:
        """Reads content."""
        return self._content


class TestWarcRecord(TestCase):
    """Test cases for WarcRecord class."""
    
    def test_from_warc_record(self):
        """Tests creation from warcio record."""
        # Test data
        record_id = '<urn:uuid:12345678>'
        target_uri = 'http://example.com'
        content_type = 'text/html'
        date_str = '2025-01-23T12:34:56Z'
        content = b'<html><body>test</body></html>'
        
        # Create mock warcio record
        headers = {
            'WARC-Record-ID': record_id,
            'WARC-Target-URI': target_uri,
            'Content-Type': content_type,
            'WARC-Date': date_str,
            'Content-Length': str(len(content)),
            'WARC-Concurrent-To': '<urn:uuid:87654321>',
            'WARC-IP-Address': '127.0.0.1',
            'WARC-Payload-Type': 'text/html',
            'WARC-Payload-Digest': 'sha1:1234567890',
            'WARC-Identified-Payload-Type': 'text/html',
            'WARC-Truncated': 'length'
        }
        http_headers = {'Content-Type': content_type}
        mock_record = MockWarcRecord('response', headers, http_headers, content)
        
        # Convert to our WarcRecord
        record = WarcRecord.from_warc_record(mock_record)
        
        # Verify all fields
        self.assertEqual(record.record_id, WarcRecordId(record_id))
        self.assertEqual(record.record_type, 'response')
        self.assertEqual(str(record.target_uri), target_uri)
        self.assertEqual(str(record.content_type), content_type)
        self.assertEqual(record.content, content.decode('utf-8'))
        self.assertEqual(record.content_length, len(content))
        self.assertEqual(record.date.strftime('%Y-%m-%dT%H:%M:%SZ'), date_str)
        self.assertEqual(record.concurrent_to, 
                        WarcRecordId('<urn:uuid:87654321>'))
        self.assertEqual(record.ip_address, '127.0.0.1')
        self.assertEqual(str(record.payload_type), 'text/html')
        self.assertEqual(record.payload_digest, 
                        PayloadDigest('sha1:1234567890'))
        self.assertEqual(str(record.identified_payload_type), 'text/html')
        self.assertEqual(record.truncated, 'length')
        self.assertEqual(record.headers, headers)
        self.assertEqual(record.http_headers, http_headers)
        
    def test_minimal_record(self):
        """Tests creation with minimal fields."""
        # Create mock warcio record with minimal fields
        headers = {
            'WARC-Record-ID': '<urn:uuid:12345678>',
            'WARC-Target-URI': 'http://example.com',
            'Content-Type': 'text/html',
            'WARC-Date': '2025-01-23T12:34:56Z',
            'Content-Length': '0'
        }
        mock_record = MockWarcRecord('response', headers, None, b'')
        
        # Convert to our WarcRecord
        record = WarcRecord.from_warc_record(mock_record)
        
        # Verify required fields
        self.assertIsNotNone(record.record_id)
        self.assertIsNotNone(record.record_type)
        self.assertIsNotNone(record.target_uri)
        self.assertIsNotNone(record.date)
        self.assertIsNotNone(record.content_type)
        self.assertEqual(record.content, '')
        self.assertEqual(record.content_length, 0)
        
        # Verify optional fields are None
        self.assertIsNone(record.concurrent_to)
        self.assertIsNone(record.ip_address)
        self.assertIsNone(record.payload_type)
        self.assertIsNone(record.payload_digest)
        self.assertIsNone(record.identified_payload_type)
        self.assertIsNone(record.truncated)
        self.assertIsNone(record.http_headers)


if __name__ == '__main__':
    unittest.main()
