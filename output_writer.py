"""Output writer interface.

This module defines the interface for writing processed WARC records to output.
Writers implementing this interface can store records in different formats.
"""

from abc import ABC, abstractmethod

from models.warc_record import ProcessedWarcRecord


class OutputWriter(ABC):
    """Interface for writing processed records to output.

    This abstract base class defines the interface that all output writers must
    implement. Each writer is responsible for:
    1. Managing its output destination (file, database, etc.)
    2. Formatting the processed records appropriately
    3. Handling any errors that occur during writing
    """

    @abstractmethod
    def configure(self, output_path: str):
        """Configure the writer with output path and any other settings.

        Args:
            output_path: Path to output file or URI for output destination.

        Raises:
            ValueError: If output path is invalid.
            PermissionError: If output destination is not writable.
        """
        pass

    @abstractmethod
    def write_record(self, record: ProcessedWarcRecord):
        """Write processed record to output.

        Args:
            record: ProcessedWarcRecord being written. Contains both the original
                WARC record metadata and the processed content.

        Raises:
            ValueError: If writer is not configured or record is invalid.
            IOError: If writing fails.
        """
        pass
