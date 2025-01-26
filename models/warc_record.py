"""WARC record models.

This module provides models for representing WARC records and their processed
versions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

from models.warc_identifiers import (PayloadDigest, WarcRecordId, WarcUri)
from models.warc_mime_types import ContentType


@dataclass
class WarcIdentifiers:
    """Represents WARC record identifiers."""
    record_id: WarcRecordId
    target_uri: WarcUri
    concurrent_to: Optional[WarcRecordId] = None


@dataclass
class WarcMetadata:
    """Represents WARC record metadata."""
    identifiers: WarcIdentifiers
    record_type: str
    date: datetime
    payload_digest: Optional[PayloadDigest] = None
    ip_address: Optional[str] = None
    truncated: Optional[str] = None


@dataclass
class WarcContent:
    """Represents WARC record content."""
    content: str
    content_type: ContentType
    content_length: int
    payload_type: Optional[ContentType] = None
    identified_payload_type: Optional[ContentType] = None


@dataclass
class WarcHeaders:
    """Represents WARC record headers."""
    warc_headers: Dict[str, str]
    http_headers: Optional[Dict[str, str]] = None


# TODO(dsullivan): Consider refactoring WarcRecord to reduce number of instance
# attributes, possibly by grouping related fields into nested structures.
# pylint: disable=too-many-instance-attributes
@dataclass
class WarcRecord:
    """Represents a WARC record.

    A structured representation combining:
    1. Record metadata (ID, type, URI, date)
    2. Content information (type, length, raw content)
    3. Headers (WARC and HTTP headers)
    """
    record_id: WarcRecordId
    record_type: str
    target_uri: WarcUri
    date: datetime
    content: str
    content_type: ContentType
    headers: Dict[str, str] = field(default_factory=dict)
    payload_digest: Optional[PayloadDigest] = None

    @property
    def content_length(self) -> int:
        """Get the content length.

        Returns:
            Length of the content.
        """
        return len(self.content)

    @property
    def date_str(self) -> str:
        """Get the date as an ISO 8601 formatted string.

        Returns:
            Date in ISO 8601 format with Z timezone.
        """
        return self.date.strftime('%Y-%m-%dT%H:%M:%SZ')

    def __str__(self) -> str:
        """Get string representation.

        Returns:
            String representation of record.
        """
        return (f'WARC-Target-URI: {self.target_uri}\n'
                f'WARC-Date: {self.date_str}\n'
                f'Content-Type: {self.content_type}\n\n'
                f'{self.content}\n\n')

    def __init__(self, **kwargs):
        """Initialize WarcRecord.
        
        Supports both direct field initialization and nested object
        initialization.
        """
        if 'metadata' in kwargs:
            # Initialize from nested objects
            metadata = kwargs['metadata']
            content = kwargs['content']
            headers = kwargs['headers']
            self.record_id = metadata.identifiers.record_id
            self.record_type = metadata.record_type
            self.target_uri = metadata.identifiers.target_uri
            self.date = metadata.date
            self.content_type = content.content_type
            self.content = content.content
            self.headers = headers.warc_headers
            self.payload_digest = metadata.payload_digest
        else:
            # Initialize from direct fields
            self.record_id = WarcRecordId(kwargs['record_id'])
            self.record_type = kwargs['record_type']
            uri = kwargs['target_uri']
            if isinstance(uri, str):
                self.target_uri = WarcUri.from_str(uri)
            else:
                self.target_uri = uri

            date = kwargs['date']
            date_fmt = '%Y-%m-%dT%H:%M:%SZ'
            if isinstance(date, str):
                self.date = datetime.strptime(date, date_fmt)
            else:
                self.date = date

            ctype = kwargs['content_type']
            if isinstance(ctype, str):
                self.content_type = ContentType(ctype)
            else:
                self.content_type = ctype

            self.content = kwargs['content']
            self.headers = kwargs.get('headers', {})
            digest = kwargs.get('payload_digest')
            if digest is not None and isinstance(digest, str):
                self.payload_digest = PayloadDigest(digest)
            else:
                self.payload_digest = digest

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
        if not record or record.rec_type != 'response':
            raise ValueError("Invalid record type")

        # Extract required fields
        record_id = WarcRecordId(
            record.rec_headers.get_header('WARC-Record-ID'))
        target_uri = WarcUri.from_str(
            record.rec_headers.get_header('WARC-Target-URI'))
        date_str = record.rec_headers.get_header('WARC-Date')
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')

        # Get content info
        content_type = ContentType(
            record.http_headers.get_header('Content-Type', 'text/html'))
        content = record.content_stream().read().decode('utf-8')

        # Get optional fields
        payload_digest = None
        if record.rec_headers.get_header('WARC-Payload-Digest'):
            payload_digest = PayloadDigest(
                record.rec_headers.get_header('WARC-Payload-Digest'))

        # Build headers dict
        headers = {}
        if record.http_headers:
            for name, value in record.http_headers.headers:
                headers[name] = value

        return cls(record_id=record_id,
                   record_type=record.rec_type,
                   target_uri=target_uri,
                   date=date,
                   content_type=content_type,
                   content=content,
                   headers=headers,
                   payload_digest=payload_digest)


@dataclass
class ProcessedWarcRecord:
    """Represents a processed WARC record.

    This class combines the original WARC record with its processed content
    and any additional metadata from processing.
    """

    record: WarcRecord
    processed_content: str
    metadata: Optional[Dict[str, str]] = None

    def __str__(self) -> str:
        """Get string representation.

        Returns:
            String representation of processed record.
        """
        return (f'WARC-Target-URI: {self.record.target_uri}\n'
                f'WARC-Date: {self.record.date_str}\n'
                f'Content-Type: {self.record.content_type}\n\n'
                f'{self.processed_content}\n\n')

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
    def from_record(
            cls,
            record: WarcRecord,
            processed_content: str,
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

        return cls(record=record,
                   processed_content=processed_content,
                   metadata=metadata)
