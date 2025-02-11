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
    def _validate_record_type(
        self, record: ArcWarcRecord
    ) -> bool:
        """Validate record type and status.

        Args:
            record: Raw WARC record from warcio.

        Returns:
            True if record type and status are valid, False otherwise.
        """
        if not record or record.rec_type != "response":
            logger.debug("Not a response record")
            return False

        if isinstance(record.http_headers, StatusAndHeaders):
            status = record.http_headers.get_statuscode()
            if status != "200":
                logger.debug("Skipping non-200 response: %s", status)
                return False
        elif record.http_headers is None:
            logger.debug("Record has no HTTP headers")
            return False

        return True

    def _extract_required_fields(
        self, record: ArcWarcRecord
    ) -> Optional[tuple]:
        """Extract required fields from record.

        Args:
            record: Raw WARC record from warcio.

        Returns:
            Tuple of (record_id, target_uri, date) if successful, None if
            missing fields.
        """
        headers = record.rec_headers
        record_id = WarcRecordId(
            headers.get_header("WARC-Record-ID")
        )
        target_uri = WarcUri.from_str(
            headers.get_header("WARC-Target-URI")
        )
        date = headers.get_header("WARC-Date")

        if not all([target_uri, date]):
            if not target_uri:
                logger.debug("Missing required field: WARC-Target-URI")
            if not date:
                logger.debug("Missing required field: WARC-Date")
            return None

        return record_id, target_uri, date

    def _extract_content(self, record: ArcWarcRecord) -> Optional[tuple]:
        """Extract content and content type from record.

        Args:
            record: Raw WARC record from warcio.

        Returns:
            Tuple of (content, content_type) if successful, None if
            extraction fails.
        """
        try:
            http_headers = record.http_headers
            default_type = "text/html"
            content_type = ContentType(
                http_headers.get_header("Content-Type", default_type)
            )

            stream = record.content_stream()
            if stream is None:
                logger.debug("Record has no content stream")
                return None

            content = stream.read()
            if not content:
                logger.debug("Record content stream is empty")
                return None

            try:
                content = content.decode("utf-8", errors="ignore")
            except UnicodeDecodeError as e:
                logger.debug("Failed to decode content: %s", str(e))
                return None

            return content, content_type

        except (AttributeError, IOError) as e:
            logger.debug("Failed to access content stream: %s", str(e))
            return None

    def _build_headers_dict(self, http_headers: StatusAndHeaders) -> dict:
        """Build headers dictionary from StatusAndHeaders object.

        Args:
            http_headers: StatusAndHeaders object from warcio.

        Returns:
            Dictionary of header name-value pairs.
        """
        response_headers = {}
        if isinstance(http_headers, StatusAndHeaders):
            for name, value in http_headers.headers:
                response_headers[name] = value
        return response_headers

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
            # Validate record type and status
            if not self._validate_record_type(record):
                return None

            # Extract required fields
            fields = self._extract_required_fields(record)
            if fields is None:
                return None
            record_id, target_uri, date = fields

            # Extract content
            content_info = self._extract_content(record)
            if content_info is None:
                return None
            content, content_type = content_info

            # Get optional fields
            payload_digest = record.rec_headers.get_header(
                "WARC-Payload-Digest"
            )
            if payload_digest:
                payload_digest = PayloadDigest(payload_digest)

            # Build headers dict
            response_headers = self._build_headers_dict(record.http_headers)

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

        except (ValueError, URLError) as e:
            logger.debug("Failed to parse record: %s", str(e))
            return None
