"""Processing statistics for WARC records.

This module tracks statistics during WARC file processing.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


# pylint: disable=too-many-instance-attributes
class ProcessingStats:
    """Tracks statistics during WARC file processing.

    Attributes:
        start_time (datetime): Time when processing started
        end_time (datetime): Time when processing finished
        input_size (int): Size of input file in bytes
        input_size_mb (float): Size of input file in MB
        bytes_processed (int): Number of bytes processed
        records_parsed (int): Number of records successfully parsed
        records_processed (int): Number of records successfully processed
        records_skipped (int): Number of records skipped
        records_failed (int): Number of records that failed processing
    """

    def __init__(self):
        """Initialize processing stats."""
        self.start_time = None
        self.end_time = None
        self.input_size = 0
        self.input_size_mb = 0.0
        self.bytes_processed = 0
        self.records_parsed = 0
        self.records_processed = 0
        self.records_skipped = 0
        self.records_failed = 0

    def reset_stats(self) -> None:
        """Reset all statistics to initial values."""
        # Create a new instance and copy its attributes
        new_stats = ProcessingStats()
        for attr, value in new_stats.__dict__.items():
            setattr(self, attr, value)

    def set_input_size(self, input_path: str) -> None:
        """Set input file size (deprecated, use start_processing instead).

        Args:
            input_path (str): Path to input file

        Raises:
            FileNotFoundError: If input file does not exist
            ValueError: If input file is empty
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        self.start_time = datetime.now()
        self.input_size = os.path.getsize(input_path)
        if self.input_size == 0:
            raise ValueError(f"Input file is empty: {input_path}")

        self.input_size_mb = self.input_size / (1024 * 1024)

    def start_processing(self, input_path: str) -> None:
        """Start processing and set input size.

        Args:
            input_path (str): Path to input file

        Raises:
            FileNotFoundError: If input file does not exist
            ValueError: If input file is empty
        """
        self.set_input_size(input_path)

    def finish_processing(self) -> None:
        """Record end time."""
        self.end_time = datetime.now()

    def track_bytes_processed(self, bytes_count: int) -> None:
        """Track number of bytes processed.

        Args:
            bytes_count (int): Number of bytes processed

        Raises:
            ValueError: If bytes_count is negative
        """
        if bytes_count < 0:
            raise ValueError("Bytes processed cannot be negative")
        self.bytes_processed += bytes_count

    def track_parsed_record(self) -> None:
        """Track successfully parsed record."""
        self.records_parsed += 1

    def track_processed_record(self) -> None:
        """Track successfully processed record."""
        self.records_processed += 1

    def track_skipped_record(self) -> None:
        """Track skipped record."""
        self.records_skipped += 1

    def track_failed_record(self) -> None:
        """Track failed record."""
        self.records_failed += 1

    def get_processing_time(self) -> timedelta:
        """Get total processing time.

        Returns:
            Time elapsed between start and end
        """
        if not self.start_time or not self.end_time:
            return timedelta()
        return self.end_time - self.start_time

    def get_processing_rate(self) -> Optional[float]:
        """Get processing rate in MB/s.

        Returns:
            Processing rate in MB/s, or None if processing hasn't finished
        """
        if not self.start_time or not self.end_time:
            return None

        processing_time = self.get_processing_time().total_seconds()
        if processing_time <= 0:
            return None

        return self.input_size_mb / processing_time

    def _update_progress(self, force: bool = False) -> None:
        """Update progress tracking.

        Args:
            force (bool): If True, update progress regardless of interval.
        """
        if not self.start_time:
            return

        current_time = datetime.now()
        if (not force and
            (current_time - self.start_time) < timedelta(seconds=1)):
            return

        total = (self.records_processed + self.records_skipped +
                 self.records_failed)

        # Log progress every 100 records or when forced
        if total % 100 == 0 or force:
            mb_processed = self.bytes_processed / (1024 * 1024)

            # Calculate percent complete and processing rate
            if self.input_size > 0:
                pct = 100.0 * self.bytes_processed / self.input_size
            else:
                pct = 0

            rate = self.get_processing_rate()
            rate_str = f", {rate:.1f} MB/s" if rate else ""

            # Break long log message into multiple lines
            msg = "Processed %d records (%.1f/%.1f MB, %.1f%%%s)"
            logger.info(msg, total, mb_processed, self.input_size_mb, pct,
                        rate_str)

    def get_summary(self) -> dict:
        """Get summary of processing statistics.

        Returns:
            Dictionary containing processing statistics
        """
        return {
            'records_parsed': self.records_parsed,
            'records_processed': self.records_processed,
            'records_skipped': self.records_skipped,
            'records_failed': self.records_failed,
            'bytes_processed': self.bytes_processed,
            'input_size': self.input_size,
            'input_size_mb': self.input_size_mb,
            'processing_time': self.get_processing_time(),
            'processing_rate': self.get_processing_rate()
        }
