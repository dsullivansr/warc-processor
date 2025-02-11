"""JSON writer implementation.

This module provides a concrete implementation of the OutputWriter interface
that writes processed WARC records to a JSON file.
"""

import json
import logging
import os

from models.warc_record import ProcessedWarcRecord
from output_writer import OutputWriter

logger = logging.getLogger(__name__)


class JsonWriter(OutputWriter):
    """Writes processed records to a JSON file.

    This writer creates a JSON file containing an array of processed WARC
    records,
    where each record includes its metadata and processed content.
    """

    def __init__(self):
        """Initialize the JSON writer."""
        self.output_path = None
        self.first_record = True

    def configure(self, output_path: str):
        """Configure the writer with output path.

        Args:
            output_path: Path to output file. Parent directory must exist and be
                writable.

        Raises:
            ValueError: If output directory does not exist.
            PermissionError: If output directory is not writable.
        """
        # Validate output directory exists
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            logger.error("Output directory does not exist: %s", output_dir)
            raise ValueError(f"Output directory does not exist: {output_dir}")

        # Check if directory is writable
        if not os.access(output_dir, os.W_OK):
            logger.error("Output directory is not writable: %s", output_dir)
            raise PermissionError(f"Output directory is not writable: {output_dir}")

        self.output_path = output_path

        # Initialize the JSON array
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("[\n")

    def write_record(self, record: ProcessedWarcRecord):
        """Write processed record to output.

        Args:
            record: ProcessedWarcRecord being written. Must contain both the
                original WARC record metadata and the processed content.

        Raises:
            ValueError: If writer is not configured or record is invalid.
        """
        if not self.output_path:
            raise ValueError("Writer is not configured")

        # Create JSON object for the record
        record_json = {
            "warc_type": record.record.record_type,
            "record_id": str(record.record.record_id),
            "date": record.record.date.isoformat() + "+00:00",
            "target_uri": str(record.record.target_uri),
            "content_type": str(record.record.content_type),
            "content": record.processed_content,
            "headers": record.record.headers,
            "metadata": record.metadata if record.metadata else {}
        }

        with open(self.output_path, "a", encoding="utf-8") as f:
            if not self.first_record:
                f.write(",\n")
            json.dump(record_json, f, indent=2)
            self.first_record = False

    def __del__(self):
        """Close the JSON array when the writer is destroyed."""
        if self.output_path and os.path.exists(self.output_path):
            with open(self.output_path, "a", encoding="utf-8") as f:
                f.write("\n]")
