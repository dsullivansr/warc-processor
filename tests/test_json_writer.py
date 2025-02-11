"""Tests for JsonWriter."""

import json
import os
import tempfile
import unittest
import shutil

from models.warc_record import WarcRecord, ProcessedWarcRecord
from writers.json_writer import JsonWriter


class TestJsonWriter(unittest.TestCase):
    """Test JSON writer implementation."""

    def setUp(self):
        """Set up test case."""
        self.output_dir = tempfile.mkdtemp()
        self.output_path = os.path.join(self.output_dir, "output.json")
        self.record = WarcRecord(
            record_type="response",
            target_uri="https://example.com",
            date="2020-01-01T00:00:00Z",
            content_type="text/html",
            payload_digest="sha1:1234",
            record_id="<urn:uuid:1234>",
            content="<html><body>Test content</body></html>",
            headers={
                "Content-Type": "text/html",
                "WARC-IP-Address": "127.0.0.1",
                "WARC-Concurrent-To": "<urn:uuid:5678>",
            },
        )

    def tearDown(self):
        """Clean up test case."""
        if os.path.exists(self.output_path):
            os.remove(self.output_path)
        shutil.rmtree(self.output_dir)

    def test_write_record_json_format(self):
        """Test writing a record in JSON format."""
        processed_record = ProcessedWarcRecord(
            record=self.record,
            processed_content="processed content",
            metadata={"test_key": "test_value"}
        )

        writer = JsonWriter()
        writer.configure(self.output_path)
        writer.write_record(processed_record)

        # Force writer cleanup to close JSON array
        del writer

        # Verify file was created and contains valid JSON
        self.assertTrue(os.path.exists(self.output_path))
        with open(self.output_path, "r", encoding="utf-8") as f:
            content = json.load(f)

            # Should be an array with one record
            self.assertIsInstance(content, list)
            self.assertEqual(len(content), 1)

            record = content[0]
            # Verify all fields are present and correct
            self.assertEqual(record["warc_type"], "response")
            self.assertEqual(record["record_id"], "<urn:uuid:1234>")
            self.assertEqual(record["date"], "2020-01-01T00:00:00+00:00")
            self.assertEqual(record["target_uri"], "https://example.com")
            self.assertEqual(record["content_type"], "text/html")
            self.assertEqual(record["content"], "processed content")
            self.assertEqual(record["metadata"], {"test_key": "test_value"})

            # Verify headers are preserved
            self.assertEqual(record["headers"]["Content-Type"], "text/html")
            self.assertEqual(record["headers"]["WARC-IP-Address"], "127.0.0.1")
            concurrent_to = record["headers"]["WARC-Concurrent-To"]
            self.assertEqual(concurrent_to, "<urn:uuid:5678>")

    def test_multiple_records_json_format(self):
        """Test writing multiple records in JSON format."""
        writer = JsonWriter()
        writer.configure(self.output_path)

        for i in range(3):
            processed_record = ProcessedWarcRecord(
                record=self.record,
                processed_content=f"content {i}",
                metadata={"record_number": i}
            )
            writer.write_record(processed_record)

        # Force writer cleanup to close JSON array
        del writer

        # Verify all records were written in JSON format
        with open(self.output_path, "r", encoding="utf-8") as f:
            content = json.load(f)

            # Should be an array with three records
            self.assertIsInstance(content, list)
            self.assertEqual(len(content), 3)

            for i, record in enumerate(content):
                # Verify all fields are present and correct
                self.assertEqual(record["warc_type"], "response")
                self.assertEqual(record["record_id"], "<urn:uuid:1234>")
                self.assertEqual(record["date"], "2020-01-01T00:00:00+00:00")
                self.assertEqual(record["target_uri"], "https://example.com")
                self.assertEqual(record["content_type"], "text/html")
                self.assertEqual(record["content"], f"content {i}")
                self.assertEqual(record["metadata"], {"record_number": i})

                # Verify headers are preserved
                self.assertEqual(record["headers"]["Content-Type"], "text/html")
                self.assertEqual(record["headers"]["WARC-IP-Address"], "127.0.0.1")
                concurrent_to = record["headers"]["WARC-Concurrent-To"]
                self.assertEqual(concurrent_to, "<urn:uuid:5678>")

    def test_write_without_configure(self):
        """Test writing without configuring first."""
        writer = JsonWriter()
        processed_record = ProcessedWarcRecord(
            record=self.record,
            processed_content="test"
        )

        with self.assertRaises(ValueError):
            writer.write_record(processed_record)

    def test_configure_bad_path(self):
        """Test configuring with invalid path."""
        writer = JsonWriter()
        with self.assertRaises(ValueError):
            writer.configure("/nonexistent/directory/file.json")


if __name__ == "__main__":
    unittest.main()
