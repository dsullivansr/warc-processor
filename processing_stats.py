"""Processing statistics tracking.

This module provides functionality for tracking and reporting WARC processing
statistics.
"""

import logging
import os
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class ProcessingStats:
    """Tracks statistics about WARC file processing.

    This class maintains counts and other metrics about the processing of WARC
    records, including:
    - Total records processed, skipped, and failed
    - Bytes processed
    - Input file size
    - Percentage of completion

    It also provides functionality for periodic progress reporting.
    """

    def __init__(self):
        """Initialize processing statistics."""
        self.reset_stats()

        # Configure progress reporting
        self.progress_interval = 100  # Records between progress updates
        self.progress_update_interval = 1.0  # Seconds between progress updates
        self.last_progress_time = 0

    def reset_stats(self):
        """Reset all statistics to initial values."""
        # Record counts
        self.records_parsed = 0
        self.records_processed = 0
        self.records_skipped = 0
        self.records_failed = 0

        # Size tracking
        self.bytes_processed = 0
        self.input_size = 0
        self.input_size_mb = 0

    def set_input_size(self, input_path: str):
        """Set input file size for progress tracking.

        Args:
            input_path: Path to input WARC file.
        """
        self.input_size = os.path.getsize(input_path)
        self.input_size_mb = self.input_size / (1024 * 1024)  # Convert to MB

    def track_bytes_processed(self, bytes_processed: int):
        """Update bytes processed count.

        Args:
            bytes_processed: Total bytes processed so far.
        """
        self.bytes_processed = bytes_processed

    def track_parsed_record(self):
        """Increment count of parsed records."""
        self.records_parsed += 1

    def track_processed_record(self):
        """Increment count of successfully processed records."""
        self.records_processed += 1

    def track_skipped_record(self):
        """Increment count of skipped records."""
        self.records_skipped += 1

    def track_failed_record(self):
        """Increment count of failed records."""
        self.records_failed += 1

    def _update_progress(self, force: bool = False):
        """Update progress tracking.

        Args:
            force: If True, update progress regardless of interval.
        """
        current_time = time.time()
        if (not force and
                (current_time - self.last_progress_time) <
                self.progress_update_interval):
            return

        total_records = (self.records_processed +
                        self.records_skipped +
                        self.records_failed)
        if total_records % self.progress_interval == 0 or force:
            mb_processed = self.bytes_processed / (1024 * 1024)

            # Calculate percent complete
            percent_complete = 0
            if self.input_size_mb > 0:
                percent_complete = (mb_processed / self.input_size_mb) * 100

            logger.info(
                "Processed %d records (%.1f/%.1f MB, %.1f%%)",
                total_records,
                mb_processed,
                self.input_size_mb,
                percent_complete
            )
            self.last_progress_time = current_time

    def get_summary(self) -> dict:
        """Get summary of processing statistics.

        Returns:
            Dictionary with statistics summary.
        """
        return {
            'records_parsed': self.records_parsed,
            'records_processed': self.records_processed,
            'records_skipped': self.records_skipped,
            'records_failed': self.records_failed,
            'bytes_processed': self.bytes_processed,
            'input_size': self.input_size,
            'input_size_mb': self.input_size_mb
        }
