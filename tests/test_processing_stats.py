"""Tests for ProcessingStats."""

import os
import tempfile
import unittest

from processing_stats import ProcessingStats


class TestProcessingStats(unittest.TestCase):
    """Test cases for ProcessingStats."""

    def setUp(self):
        """Set up test fixtures."""
        self.stats = ProcessingStats()
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(b'test content')
        self.temp_file.close()

    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_file.name)

    def test_initial_stats(self):
        """Test initial statistics values."""
        summary = self.stats.get_summary()
        self.assertEqual(summary['records_processed'], 0)
        self.assertEqual(summary['records_parsed'], 0)
        self.assertEqual(summary['records_skipped'], 0)
        self.assertEqual(summary['records_failed'], 0)
        self.assertEqual(summary['input_size'], 0)
        self.assertEqual(summary['input_size_mb'], 0.0)

    def test_track_processed_record(self):
        """Test tracking processed record."""
        self.stats.track_processed_record()
        summary = self.stats.get_summary()
        self.assertEqual(summary['records_processed'], 1)
        self.assertEqual(summary['records_parsed'], 0)
        self.assertEqual(summary['records_skipped'], 0)
        self.assertEqual(summary['records_failed'], 0)

    def test_track_parsed_record(self):
        """Test tracking parsed record."""
        self.stats.track_parsed_record()
        summary = self.stats.get_summary()
        self.assertEqual(summary['records_processed'], 0)
        self.assertEqual(summary['records_parsed'], 1)
        self.assertEqual(summary['records_skipped'], 0)
        self.assertEqual(summary['records_failed'], 0)

    def test_track_skipped_record(self):
        """Test tracking skipped record."""
        self.stats.track_skipped_record()
        summary = self.stats.get_summary()
        self.assertEqual(summary['records_processed'], 0)
        self.assertEqual(summary['records_parsed'], 0)
        self.assertEqual(summary['records_skipped'], 1)
        self.assertEqual(summary['records_failed'], 0)

    def test_track_failed_record(self):
        """Test tracking failed record."""
        self.stats.track_failed_record()
        summary = self.stats.get_summary()
        self.assertEqual(summary['records_processed'], 0)
        self.assertEqual(summary['records_parsed'], 0)
        self.assertEqual(summary['records_skipped'], 0)
        self.assertEqual(summary['records_failed'], 1)

    def test_set_input_size(self):
        """Test setting input size."""
        self.stats.set_input_size(self.temp_file.name)
        summary = self.stats.get_summary()
        self.assertEqual(summary['input_size'], len(b'test content'))
        self.assertGreater(summary['input_size_mb'], 0)

    def test_reset_stats(self):
        """Test resetting statistics."""
        # Add some stats
        self.stats.track_processed_record()
        self.stats.track_parsed_record()
        self.stats.track_skipped_record()
        self.stats.track_failed_record()
        self.stats.set_input_size(self.temp_file.name)

        # Reset stats
        self.stats.reset_stats()

        # Verify reset
        summary = self.stats.get_summary()
        self.assertEqual(summary['records_processed'], 0)
        self.assertEqual(summary['records_parsed'], 0)
        self.assertEqual(summary['records_skipped'], 0)
        self.assertEqual(summary['records_failed'], 0)
        self.assertEqual(summary['input_size'], 0)
        self.assertEqual(summary['input_size_mb'], 0.0)

    def test_multiple_records(self):
        """Test tracking multiple records."""
        # Track multiple records
        for _ in range(3):
            self.stats.track_processed_record()
        for _ in range(4):
            self.stats.track_parsed_record()
        for _ in range(2):
            self.stats.track_skipped_record()
        self.stats.track_failed_record()

        # Verify counts
        summary = self.stats.get_summary()
        self.assertEqual(summary['records_processed'], 3)
        self.assertEqual(summary['records_parsed'], 4)
        self.assertEqual(summary['records_skipped'], 2)
        self.assertEqual(summary['records_failed'], 1)

    def test_record_processing_flow(self):
        """Test typical record processing flow."""
        # Simulate processing a record:
        # 1. Record is parsed
        # 2. Record is processed
        self.stats.track_parsed_record()
        self.stats.track_processed_record()

        # Simulate processing a record that is skipped:
        # 1. Record is parsed
        # 2. Record is skipped
        self.stats.track_parsed_record()
        self.stats.track_skipped_record()

        # Simulate processing a record that fails:
        # 1. Record is parsed
        # 2. Record fails processing
        self.stats.track_parsed_record()
        self.stats.track_failed_record()

        # Verify final state
        summary = self.stats.get_summary()
        self.assertEqual(summary['records_parsed'], 3)
        self.assertEqual(summary['records_processed'], 1)
        self.assertEqual(summary['records_skipped'], 1)
        self.assertEqual(summary['records_failed'], 1)


if __name__ == '__main__':
    unittest.main()
