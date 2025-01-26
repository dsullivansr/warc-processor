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
            content_length=100,
            headers={'Content-Type': 'text/html'})

    def tearDown(self):
        """Clean up test case."""
        if os.path.exists(self.output_path):
            os.remove(self.output_path)
        shutil.rmtree(self.output_dir)

    def test_write_record(self):
        """Test writing a record."""
        processed_record = ProcessedWarcRecord.from_record(
            self.record, 'processed content')

        writer = PlainTextWriter()
        writer.configure(self.output_path)
        writer.write_record(processed_record)

        # Verify file was created and contains content
        self.assertTrue(os.path.exists(self.output_path))
        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('WARC-Target-URI: https://example.com', content)
            self.assertIn('WARC-Date: 2020-01-01T00:00:00Z', content)
            self.assertIn('Content-Type: text/html', content)
            self.assertIn('processed content', content)

    def test_multiple_writes(self):
        """Test writing multiple records."""
        writer = PlainTextWriter()
        writer.configure(self.output_path)

        for i in range(3):
            processed_record = ProcessedWarcRecord.from_record(
                self.record, f'content {i}')
            writer.write_record(processed_record)

        # Verify all records were written
        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertEqual(content.count('WARC-Target-URI'), 3)
            self.assertEqual(content.count('content 0'), 1)
            self.assertEqual(content.count('content 1'), 1)
            self.assertEqual(content.count('content 2'), 1)

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
