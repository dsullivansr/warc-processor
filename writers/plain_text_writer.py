"""Plain text writer implementation.

This module provides a concrete implementation of the OutputWriter interface
that writes processed WARC records to a plain text file in WARC format.
"""

import logging
import os

from models.warc_record import ProcessedWarcRecord
from output_writer import OutputWriter

logger = logging.getLogger(__name__)


class PlainTextWriter(OutputWriter):
    """Writes processed records to a plain text file.

    This writer creates a text file containing just the processed text content
    from each WARC record, with records separated by YAML document
    separators (---)
    to handle multi-line content safely.
    """

    def __init__(self):
        """Initialize the plain text writer."""
        self.output_path = None

    def configure(self, output_path: str):
        """Configure the writer with output path and any other settings.

        Args:
            output_path: Path to output file. Parent directory must exist and be
                writable.

        Raises:
            ValueError: If output directory does not exist.
            PermissionError: If output directory is not writable.
        """
        # Validate output directory
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            raise ValueError(f"Output directory does not exist: {output_dir}")
        if not os.access(output_dir, os.W_OK):
            raise PermissionError(
                f"Output directory is not writable: {output_dir}"
            )

        # Create empty file
        with open(output_path, "w", encoding="utf-8"):
            pass

        self.output_path = output_path

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

        with open(self.output_path, "a", encoding="utf-8") as f:
            # Start WARC record
            f.write("WARC/1.0\n")
            # Write WARC record header
            f.write(f"WARC-Type: {record.record.record_type}\n")
            f.write(f"WARC-Target-URI: {record.record.target_uri}\n")
            warc_date = record.record.date.strftime('%Y-%m-%dT%H:%M:%SZ')
            f.write(f"WARC-Date: {warc_date}\n")
            f.write(f"WARC-Record-ID: {record.record.record_id}\n")
            if record.record.payload_digest:
                f.write(f"WARC-Payload-Digest: {record.record.payload_digest}\n")
            # Write additional headers from the original record
            for header_name, header_value in record.record.headers.items():
                if not header_name.startswith('Content-Length'):
                    f.write(f"{header_name}: {header_value}\n")
            content_bytes = record.processed_content.encode('utf-8')
            f.write(f"Content-Length: {len(content_bytes)}\n")
            f.write("\n")
            f.write(record.processed_content)
            f.write("\n")
            # End WARC record
            f.write("WARC/1.0\n\n")
