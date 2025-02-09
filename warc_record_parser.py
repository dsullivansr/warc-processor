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


# TODO(dsullivan): Consider extracting common record creation code into a shared
# utility. For now, keeping it duplicated since it represents core WARC fields
# and extracting it would add complexity.
# pylint: disable=duplicate-code
class WarcRecordParser:
    """Parser for converting warcio records to WarcRecord objects.

    This class handles the conversion of raw WARC records from warcio into our
    internal WarcRecord model, including:
    1. Extracting and validating required fields
    2. Converting field values into appropriate types
    3. Building the complete WarcRecord object
    """

    # TODO(dsullivan): Consider refactoring parse method to reduce number of
    # local variables by extracting helper methods.
    # pylint: disable=too-many-locals
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
        try:
            # Early validation
            if not record or record.rec_type != "response":
                logger.debug("Not a response record")
                return None

            # Check response status
            if isinstance(record.http_headers, StatusAndHeaders):
                status = record.http_headers.get_statuscode()
                if status != "200":
                    logger.debug("Skipping non-200 response: %s", status)
                    return None

            # Extract and validate required fields
            headers = record.rec_headers
            record_id = WarcRecordId(headers.get_header("WARC-Record-ID"))
            target_uri = WarcUri.from_str(headers.get_header("WARC-Target-URI"))
            date = headers.get_header("WARC-Date")

            if not all([target_uri, date]):
                if not target_uri:
                    logger.debug("Missing required field: WARC-Target-URI")
                if not date:
                    logger.debug("Missing required field: WARC-Date")
                return None

            # Get content info
            http_headers = record.http_headers
            default_type = "text/html"
            content_type = ContentType(
                http_headers.get_header("Content-Type", default_type)
            )
            stream = record.content_stream()
            content = stream.read().decode("utf-8", errors="ignore")

            # Get optional fields
            payload_digest = headers.get_header("WARC-Payload-Digest")
            if payload_digest:
                payload_digest = PayloadDigest(payload_digest)

            # Build headers dict
            response_headers = {}
            if isinstance(http_headers, StatusAndHeaders):
                for name, value in http_headers.headers:
                    response_headers[name] = value

            # Build and return record
            return WarcRecord(
                record_id=record_id,
                record_type=record.rec_type,
                target_uri=target_uri,
                date=date,
                content_type=content_type,
                content=content,
                headers=response_headers,
                payload_digest=payload_digest,
            )

        except (
            ValueError,
            URLError,
            AttributeError,
            IOError,
            UnicodeError,
        ) as e:
            logger.debug("Failed to parse record: %s", str(e))
            return None
