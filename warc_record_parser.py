"""WARC record parser.

This module provides functionality for parsing WARC records from warcio into our
internal WarcRecord model.
"""

import logging
from typing import Optional
from urllib.error import URLError

from warcio.recordloader import ArcWarcRecord
from warcio.statusandheaders import StatusAndHeaders

from models.warc_identifiers import PayloadDigest, WarcRecordId, WarcUri
from models.warc_mime_types import ContentType
from models.warc_record import WarcRecord

logger = logging.getLogger(__name__)


class WarcRecordParser:
    """Parser for converting warcio records to WarcRecord objects.

    This class handles the conversion of raw WARC records from warcio into our
    internal WarcRecord model, including:
    1. Extracting and validating required fields
    2. Converting field values into appropriate types
    3. Building the complete WarcRecord object
    """

    def parse(self, record: ArcWarcRecord) -> Optional[WarcRecord]:
        """Parse a warcio record into a WarcRecord.

        Args:
            record: Raw WARC record from warcio.

        Returns:
            Parsed WarcRecord if successful, None if record should be skipped.

        Raises:
            ValueError: If record is missing required fields or has invalid
                values.
        """
        if not record or record.rec_type != 'response':
            return None

        try:
            # Check response status
            if isinstance(record.http_headers, StatusAndHeaders):
                status = record.http_headers.get_statuscode()
                if status != '200':
                    logger.debug("Skipping non-200 response: %s", status)
                    return None

            # Extract required fields
            record_id = WarcRecordId(
                record.rec_headers.get_header('WARC-Record-ID'))
            target_uri = WarcUri.from_str(
                record.rec_headers.get_header('WARC-Target-URI'))
            if not target_uri:
                logger.debug("Missing required field: WARC-Target-URI")
                return None

            date = record.rec_headers.get_header('WARC-Date')
            if not date:
                logger.debug("Missing required field: WARC-Date")
                return None

            # Get content info
            content_type = ContentType(
                record.http_headers.get_header('Content-Type', 'text/html'))
            try:
                stream = record.content_stream()
                content = stream.read().decode('utf-8', errors='ignore')
            except (IOError, UnicodeError) as e:
                logger.debug("Failed to read content stream: %s", str(e))
                return None

            content_length = len(content)

            # Get optional fields
            payload_digest = record.rec_headers.get_header(
                'WARC-Payload-Digest')
            if payload_digest:
                payload_digest = PayloadDigest(payload_digest)

            # Build headers dict
            headers = {}
            if isinstance(record.http_headers, StatusAndHeaders):
                for name, value in record.http_headers.headers:
                    headers[name] = value

            return WarcRecord(
                record_id=record_id,
                record_type=record.rec_type,
                target_uri=target_uri,
                date=date,
                content_type=content_type,
                content=content,
                content_length=content_length,
                headers=headers,
                payload_digest=payload_digest,
            )

        except (ValueError, URLError, AttributeError) as e:
            logger.debug("Failed to parse record: %s", str(e))
            return None
