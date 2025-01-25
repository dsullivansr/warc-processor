"""Processing statistics.

This module provides functionality for tracking statistics about WARC record
processing.
"""

import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ProcessingStats:
    """Tracks statistics about WARC record processing.

    This class maintains counters for:
    1. Number of records processed successfully
    2. Number of records skipped
    3. Number of records that failed processing
    4. Total bytes processed
    5. Number of records parsed successfully
    """

    def __init__(self):
        """Initialize processing statistics."""
        self.reset_stats()

    def reset_stats(self):
        """Reset all statistics to zero."""
        self._stats = {
            'records_processed': 0,
            'records_parsed': 0,
            'records_skipped': 0,
            'records_failed': 0,
            'input_size': 0,
            'input_size_mb': 0.0,
            'bytes_processed': 0,
        }

    def track_processed_record(self):
        """Track a successfully processed record."""
        self._stats['records_processed'] += 1

    def track_parsed_record(self):
        """Track a successfully parsed record."""
        self._stats['records_parsed'] += 1

    def track_skipped_record(self):
        """Track a skipped record."""
        self._stats['records_skipped'] += 1

    def track_failed_record(self):
        """Track a failed record."""
        self._stats['records_failed'] += 1

    def set_input_size(self, input_path: str):
        """Set input size statistics from file path.

        Args:
            input_path: Path to input file.
        """
        size_bytes = os.path.getsize(input_path)
        self._stats['input_size'] = size_bytes
        self._stats['input_size_mb'] = size_bytes / (1024 * 1024)

    @property
    def records_processed(self) -> int:
        """Get the number of records successfully processed."""
        return self._stats['records_processed']

    @property
    def records_parsed(self) -> int:
        """Get the number of records successfully parsed."""
        return self._stats['records_parsed']

    @property
    def records_skipped(self) -> int:
        """Get the number of records skipped during processing."""
        return self._stats['records_skipped']

    @property
    def records_failed(self) -> int:
        """Get the number of records that failed processing."""
        return self._stats['records_failed']

    @property
    def input_size(self) -> int:
        """Get the input file size in bytes."""
        return self._stats['input_size']

    @property
    def input_size_mb(self) -> float:
        """Get the input file size in megabytes."""
        return self._stats['input_size_mb']

    @property
    def bytes_processed(self) -> int:
        """Get the total number of bytes processed."""
        return self._stats['bytes_processed']

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of processing statistics.

        Returns:
            Dictionary containing all statistics.
        """
        return self._stats.copy()
