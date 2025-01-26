"""WARC record models.

This module provides models for representing WARC records and their processed
versions.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from models.warc_identifiers import PayloadDigest, WarcRecordId, WarcUri
from models.warc_mime_types import ContentType


@dataclass
class WarcRecord:
    """Represents a WARC record.
    
    This class provides a structured representation of a WARC record, including:
    1. Record metadata (ID, type, URI, date)
    2. Content information (type, length, raw content)
    3. Optional fields (payload digest, headers)
    """
    
    record_id: WarcRecordId
    record_type: str
    target_uri: WarcUri
    date: datetime
    content_type: ContentType
    content: str
    content_length: int
    headers: Dict[str, str]
    payload_digest: Optional[PayloadDigest] = None
    concurrent_to: Optional[WarcRecordId] = None
    ip_address: Optional[str] = None
    payload_type: Optional[ContentType] = None
    identified_payload_type: Optional[ContentType] = None
    truncated: Optional[str] = None
    http_headers: Optional[Dict[str, str]] = None
    
    @classmethod
    def from_warc_record(cls, record) -> 'WarcRecord':
        """Create WarcRecord from warcio record.
        
        Args:
            record: Raw warcio record.
            
        Returns:
            Parsed WarcRecord.
            
        Raises:
            ValueError: If record is missing required fields.
        """
        # Get required fields
        record_id = WarcRecordId(record.rec_headers.get_header('WARC-Record-ID'))
        target_uri = WarcUri.from_str(record.rec_headers.get_header('WARC-Target-URI'))
        date_str = record.rec_headers.get_header('WARC-Date')
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
        
        # Get content info
        content_type = None
        if record.http_headers:
            content_type = ContentType(record.http_headers.get_header('Content-Type', 'text/html'))
        if not content_type:
            content_type = ContentType('text/html')
            
        # Get content
        content = ''
        if record._content:
            content = record._content.decode('utf-8')
            
        # Get WARC headers
        headers = {}
        for name, value in record.rec_headers.headers:
            headers[name] = value
                
        # Get HTTP headers
        http_headers = None
        if record.http_headers:
            http_headers = {}
            for name, value in record.http_headers.headers:
                http_headers[name] = value
                
        # Build optional fields
        payload_digest = None
        if record.rec_headers.get_header('WARC-Payload-Digest'):
            payload_digest = PayloadDigest(record.rec_headers.get_header('WARC-Payload-Digest'))
            
        # Get concurrent_to
        concurrent_to = None
        if record.rec_headers.get_header('WARC-Concurrent-To'):
            concurrent_to = WarcRecordId(record.rec_headers.get_header('WARC-Concurrent-To'))
            
        # Get IP address
        ip_address = record.rec_headers.get_header('WARC-IP-Address') or None
            
        # Get payload type
        payload_type = None
        if record.rec_headers.get_header('WARC-Payload-Type'):
            payload_type = ContentType(record.rec_headers.get_header('WARC-Payload-Type'))
            
        # Get identified payload type
        identified_payload_type = None
        if record.rec_headers.get_header('WARC-Identified-Payload-Type'):
            identified_payload_type = ContentType(record.rec_headers.get_header('WARC-Identified-Payload-Type'))
            
        # Get truncated
        truncated = record.rec_headers.get_header('WARC-Truncated') or None
                
        return cls(
            record_id=record_id,
            record_type=record.rec_type,
            target_uri=target_uri,
            date=date,
            content_type=content_type,
            content=content,
            content_length=len(content),
            headers=headers,
            payload_digest=payload_digest,
            concurrent_to=concurrent_to,
            ip_address=ip_address,
            payload_type=payload_type,
            identified_payload_type=identified_payload_type,
            truncated=truncated,
            http_headers=http_headers
        )


@dataclass
class ProcessedWarcRecord:
    """Represents a processed WARC record.
    
    This class combines the original WARC record with its processed content
    and any additional metadata from processing.
    """
    
    record: WarcRecord
    processed_content: str
    metadata: Optional[Dict[str, str]] = None
    
    @property
    def url(self) -> str:
        """Get the URL of the record.
        
        Returns:
            Target URI as string.
        """
        return str(self.record.target_uri)
        
    @property
    def original_record(self) -> WarcRecord:
        """Get the original WARC record.
        
        Returns:
            Original WarcRecord.
        """
        return self.record
        
    @classmethod
    def from_record(cls, record: WarcRecord, processed_content: str,
                   metadata: Optional[Dict[str, str]] = None) -> 'ProcessedWarcRecord':
        """Create ProcessedWarcRecord from WarcRecord and processed content.
        
        Args:
            record: Original WarcRecord.
            processed_content: Content after processing.
            metadata: Optional metadata from processing.
            
        Returns:
            New ProcessedWarcRecord.
        """
        if metadata is None:
            metadata = {}
            
        return cls(
            record=record,
            processed_content=processed_content,
            metadata=metadata
        )
        
    def __str__(self):
        """Get string representation.
        
        Returns:
            Record as string with metadata and content.
        """
        parts = [
            f"URI: {self.record.target_uri}",
            f"Date: {self.record.date.strftime('%Y-%m-%dT%H:%M:%SZ')}",
            f"Content-Type: {self.record.content_type}",
            f"Content Length: {len(self.processed_content)}",
            "",
            self.processed_content
        ]
        return "\n".join(parts)
