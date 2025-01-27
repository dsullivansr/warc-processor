"""Tests for plain text writer implementation."""

import os
import tempfile
import unittest
import shutil

from models.warc_record import WarcRecord, ProcessedWarcRecord
from plain_text_writer import PlainTextWriter


class TestPlainTextWriter(unittest.TestCase):
    """Test plain text writer implementation."""

    def setUp(self):
        """Set up test case."""
        self.output_dir = tempfile.mkdtemp()
        self.output_path = os.path.join(self.output_dir, 'output.txt')
        self.record = WarcRecord(
            record_type='response',
            target_uri='https://example.com',
            date='2020-01-01T00:00:00Z',
            content_type='text/html',
            payload_digest='sha1:1234',
            record_id='<urn:uuid:1234>',
            content='<html><body>Test content</body></html>',
            headers={
                'Content-Type': 'text/html',
                'WARC-IP-Address': '127.0.0.1',
                'WARC-Concurrent-To': '<urn:uuid:5678>'
            })

    def tearDown(self):
        """Clean up test case."""
        if os.path.exists(self.output_path):
            os.remove(self.output_path)
        shutil.rmtree(self.output_dir)

    def test_write_record_warc_format(self):
        """Test writing a record in WARC format."""
        processed_record = ProcessedWarcRecord.from_record(
            self.record, 'processed content')

        writer = PlainTextWriter()
        writer.configure(self.output_path)
        writer.write_record(processed_record)

        # Verify file was created and contains content in WARC format
        self.assertTrue(os.path.exists(self.output_path))
        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Verify WARC version markers
            self.assertTrue(content.startswith('WARC/1.0\n'))
            self.assertTrue(content.strip().endswith('WARC/1.0'))

            # Verify required WARC headers are present and in correct order
            lines = content.split('\n')

            # Find where headers end (first empty line)
            header_end = lines.index('')
            headers = lines[1:header_end]  # Skip WARC/1.0

            # Verify required headers are present and in correct order
            self.assertIn('WARC-Type: response', headers)
            self.assertIn('WARC-Record-ID: <urn:uuid:1234>', headers)
            self.assertIn('WARC-Date: 2020-01-01T00:00:00Z', headers)
            self.assertIn('WARC-Target-URI: https://example.com', headers)
            self.assertIn('Content-Type: text/html', headers)
            self.assertIn('WARC-Payload-Digest: sha1:1234', headers)

            # Verify additional headers are preserved
            self.assertIn('WARC-IP-Address: 127.0.0.1', headers)
            self.assertIn('WARC-Concurrent-To: <urn:uuid:5678>', headers)

            # Verify Content-Length is present and correct
            content_length_line = next(
                line for line in headers if line.startswith('Content-Length: '))
            self.assertEqual(
                content_length_line,
                f'Content-Length: {len("processed content".encode("utf-8"))}')

            # Verify content is after blank line
            content_start = header_end + 1
            self.assertEqual(lines[content_start], 'processed content')

    def test_multiple_records_warc_format(self):
        """Test writing multiple records in WARC format."""
        writer = PlainTextWriter()
        writer.configure(self.output_path)

        for i in range(3):
            processed_record = ProcessedWarcRecord.from_record(
                self.record, f'content {i}')
            writer.write_record(processed_record)

        # Verify all records were written in WARC format
        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Should have 4 WARC/1.0 markers (start of each record + end)
            self.assertEqual(content.count('WARC/1.0'), 6)

            # Each record should be properly delimited
            records = content.split('\nWARC/1.0\n\n')[:-1]
            self.assertEqual(len(records), 3)

            for i, record in enumerate(records):
                # Each record should have all required headers
                self.assertIn('WARC-Type: response', record)
                self.assertIn('WARC-Record-ID: <urn:uuid:1234>', record)
                self.assertIn('WARC-Date: 2020-01-01T00:00:00Z', record)
                self.assertIn('WARC-Target-URI: https://example.com', record)
                self.assertIn('Content-Type: text/html', record)
                self.assertIn('WARC-Payload-Digest: sha1:1234', record)
                self.assertIn(f'content {i}', record)

                # Verify record structure (headers, blank line, content)
                record_lines = record.split('\n')
                self.assertIn('', record_lines)  # Should have blank line
                content_start = record_lines.index('') + 1
                self.assertEqual(record_lines[content_start], f'content {i}')

    def test_write_without_configure(self):
        """Test writing without configuring first."""
        writer = PlainTextWriter()
        processed_record = ProcessedWarcRecord.from_record(self.record, 'test')

        with self.assertRaises(ValueError):
            writer.write_record(processed_record)

    def test_configure_bad_path(self):
        """Test configuring with invalid path."""
        writer = PlainTextWriter()
        with self.assertRaises(ValueError):
            writer.configure('/nonexistent/directory/file.txt')


if __name__ == '__main__':
    unittest.main()
