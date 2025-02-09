"""Tests for ProcessedWarcRecord."""

from datetime import datetime
from unittest import TestCase

from models.warc_identifiers import PayloadDigest, WarcRecordId, WarcUri
from models.warc_mime_types import ContentType
from models.warc_record import ProcessedWarcRecord, WarcRecord


class TestProcessedWarcRecord(TestCase):
    """Tests for ProcessedWarcRecord."""

    def setUp(self):
        """Set up test data."""
        self.warc_record = WarcRecord(
            record_id=WarcRecordId("<urn:uuid:1234>"),
            record_type="response",
            target_uri=WarcUri.from_str("https://example.com"),
            date=datetime.strptime(
                "2025-01-23T12:34:56Z", "%Y-%m-%dT%H:%M:%SZ"
            ),
            content_type=ContentType("text/html"),
            content="Test content",
            content_length=11,
            headers={"Content-Type": "text/html"},
            payload_digest=PayloadDigest("sha1:1234"),
        )
        self.processed_content = "Processed test content"
        self.metadata = {"key": "value"}

    def test_from_warc_record(self):
        """Test creation from WarcRecord."""
        record = ProcessedWarcRecord.from_record(
            self.warc_record,
            processed_content=self.processed_content,
            metadata=self.metadata,
        )

        self.assertEqual(record.record, self.warc_record)
        self.assertEqual(record.processed_content, self.processed_content)
        self.assertEqual(record.metadata, self.metadata)

    def test_from_warc_record_no_metadata(self):
        """Test creation without metadata."""
        record = ProcessedWarcRecord.from_record(
            self.warc_record, processed_content=self.processed_content
        )

        self.assertEqual(record.record, self.warc_record)
        self.assertEqual(record.processed_content, self.processed_content)
        self.assertEqual(record.metadata, {})

    def test_str_representation(self):
        """Test string representation of ProcessedWarcRecord."""
        record = ProcessedWarcRecord.from_record(
            self.warc_record,
            processed_content=self.processed_content,
            metadata=self.metadata,
        )

        str_repr = str(record)

        self.assertIn("https://example.com", str_repr)
        self.assertIn("2025-01-23T12:34:56Z", str_repr)
        self.assertIn("text/html", str_repr)
        self.assertIn(self.processed_content, str_repr)
