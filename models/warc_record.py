"""Data models for WARC record processing.

This module provides data structures for representing WARC (Web ARChive) records
and their associated metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

from models.warc_mime_types import ContentType
from models.warc_identifiers import PayloadDigest, WarcRecordId, WarcUri


@dataclass
class WarcRecord:
    """Represents a WARC record with its essential fields.

    Attributes:
        record_id: Unique identifier for the WARC record.
        record_type: Type of WARC record (e.g., 'response', 'request').
        target_uri: Target URI of the WARC record.
        date: Timestamp of when the record was created.
        content_type: MIME type of the record content.
        content: Actual content of the record.
        content_length: Length of the content in bytes.
        headers: Dictionary of WARC headers.
        http_headers: Optional HTTP headers if present.
        concurrent_to: Optional reference to concurrent WARC record.
        ip_address: Optional IP address of the server.
        payload_type: Optional MIME type of the payload.
        payload_digest: Optional digest of the payload.
        identified_payload_type: Optional identified type of the payload.
        truncated: Optional truncation information.
        extra_fields: Optional dictionary for additional fields.
    """

    record_id: WarcRecordId
    record_type: str
    target_uri: WarcUri
    date: datetime
    content_type: ContentType
    content: str
    content_length: int
    headers: Dict[str, str]
    http_headers: Optional[Dict[str, str]] = None
    concurrent_to: Optional[WarcRecordId] = None
    ip_address: Optional[str] = None
    payload_type: Optional[ContentType] = None
    payload_digest: Optional[PayloadDigest] = None
    identified_payload_type: Optional[ContentType] = None
    truncated: Optional[str] = None
    extra_fields: Optional[Dict[str, Any]] = None

    @classmethod
    def from_warc_record(cls, record) -> 'WarcRecord':
        """Creates a WarcRecord instance from a warcio record.

        Args:
            record: A warcio.recordloader.ArcWarcRecord instance.

        Returns:
            A new WarcRecord instance populated with data from the input record.
        """
        headers = dict(record.rec_headers.headers)
        http_headers = (dict(record.http_headers.headers) if record.http_headers 
                       else None)
        
        # Get content type from HTTP headers if available
        content_type = ''
        if record.http_headers:
            content_type = record.http_headers.get_header('Content-Type', '')
        if not content_type:
            content_type = headers.get('Content-Type', '')

        # Get content from record
        content = record._content.decode('utf-8') if record._content else ''
        
        return cls(
            record_id=WarcRecordId(headers.get('WARC-Record-ID', '')),
            record_type=record.rec_type,
            target_uri=WarcUri.from_str(headers.get('WARC-Target-URI', '')),
            date=datetime.strptime(
                headers.get('WARC-Date', ''), 
                '%Y-%m-%dT%H:%M:%SZ'
            ),
            content_type=ContentType(content_type),
            content=content,
            content_length=int(headers.get('Content-Length', 0)),
            headers=headers,
            http_headers=http_headers,
            concurrent_to=(WarcRecordId(headers['WARC-Concurrent-To'])
                         if 'WARC-Concurrent-To' in headers else None),
            ip_address=headers.get('WARC-IP-Address'),
            payload_type=(ContentType(headers['WARC-Payload-Type'])
                        if 'WARC-Payload-Type' in headers else None),
            payload_digest=(PayloadDigest(headers['WARC-Payload-Digest'])
                          if 'WARC-Payload-Digest' in headers else None),
            identified_payload_type=(
                ContentType(headers['WARC-Identified-Payload-Type'])
                if 'WARC-Identified-Payload-Type' in headers else None
            ),
            truncated=headers.get('WARC-Truncated')
        )


@dataclass
class ProcessedWarcRecord:
    """Represents a processed WARC record."""
    
    record: WarcRecord
    processed_content: str
    metadata: Dict = field(default_factory=dict)
    
    @property
    def url(self) -> str:
        """Get the URL of the record."""
        return self.record.target_uri
    
    @property
    def original_record(self) -> WarcRecord:
        """Get the original WARC record."""
        return self.record
    
    @classmethod
    def from_record(cls, record: WarcRecord, processed_content: str, metadata: Optional[Dict] = None) -> 'ProcessedWarcRecord':
        """Create a processed record from a WARC record and processed content.
        
        Args:
            record: Original WARC record.
            processed_content: Processed content.
            metadata: Optional metadata dictionary.
            
        Returns:
            ProcessedWarcRecord object.
        """
        return cls(
            record=record,
            processed_content=processed_content,
            metadata=metadata or {}
        )
        
    def __str__(self) -> str:
        """Get string representation.
        
        Returns:
            String representation.
        """
        return f"ProcessedWarcRecord(url={self.url}, content_length={len(self.processed_content)})"
