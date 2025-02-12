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



    @property
    def processing_time(self) -> Optional[timedelta]:
        """Get total processing time.

        Returns:
            Total processing time or None if processing not finished
        """
        if not self.start_time or not self.end_time:
            return None
        return self.end_time - self.start_time

    @property
    def processing_speed_mb_per_sec(self) -> Optional[float]:
        """Get processing speed in MB/sec.

        Returns:
            Processing speed in MB/sec or None if processing not finished
        """
        if not self.processing_time:
            return None
        return self.input_size_mb / self.processing_time.total_seconds()

    @property
    def records_per_sec(self) -> Optional[float]:
        """Get records processed per second.

        Returns:
            Records per second or None if processing not finished
        """
        if not self.processing_time:
            return None
        return self.records_processed / self.processing_time.total_seconds()

    def get_summary_text(self) -> str:
        """Get a formatted text summary of processing statistics.

        Returns:
            Formatted string with processing statistics
        """
        if not self.processing_time:
            return "Processing not completed"

        # Remove microseconds
        time_str = str(self.processing_time).split('.', maxsplit=1)[0]
        speed = self.processing_speed_mb_per_sec or 0
        rps = self.records_per_sec or 0

        return (
            f"\nProcessing Summary:\n"
            f"  Time: {time_str}\n"
            f"  Input Size: {self.input_size_mb:.1f} MB\n"
            f"  Speed: {speed:.1f} MB/sec\n"
            f"\nRecord Statistics:\n"
            f"  Total Records: {self.records_parsed}\n"
            f"  Successfully Processed: {self.records_processed}\n"
            f"  Skipped: {self.records_skipped}\n"
            f"  Failed: {self.records_failed}\n"
            f"  Processing Rate: {rps:.1f} records/sec\n"
        )

    def get_summary(self) -> dict:
        """Get a dictionary summary of processing statistics.

        Returns:
            Dictionary containing processing statistics
        """
        return {
            "records_parsed": self.records_parsed,
            "records_processed": self.records_processed,
            "records_skipped": self.records_skipped,
            "records_failed": self.records_failed,
            "input_size": self.input_size,
            "input_size_mb": self.input_size_mb,
            "processing_time": self.processing_time,
            "processing_rate": self.processing_speed_mb_per_sec,
        }

    def track_skipped_record(self) -> None:
        """Track skipped record."""
        self.records_skipped += 1

    def track_failed_record(self) -> None:
        """Track failed record."""
        self.records_failed += 1

    def track_processed_record(self) -> None:
        """Track successfully processed record."""
        self.records_processed += 1

    def get_summary_dict(self) -> dict:
        """Get summary of processing statistics as a dictionary.

        Returns:
            Dictionary containing processing statistics
        """
        return self.get_summary()
