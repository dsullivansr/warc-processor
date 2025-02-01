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
    """Writes processed records to a plain text file in WARC format.
    
    This writer creates a text file containing the processed WARC records,
    preserving all original WARC fields and format, with the only difference
    being that the HTML content is replaced with plaintext. The format follows
    the WARC specification:
    
    WARC/1.0
    WARC-Type: [type]
    WARC-Record-ID: [id]
    WARC-Date: [date]
    WARC-Target-URI: [uri]
    Content-Type: [type]
    Content-Length: [length]
    WARC-Payload-Digest: [digest]
    [additional headers...]
    
    [processed content]
    
    WARC/1.0
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
                f"Output directory is not writable: {output_dir}")

        # Create empty file
        with open(output_path, 'w', encoding='utf-8'):
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

        with open(self.output_path, 'a', encoding='utf-8') as f:
            # Write WARC version
            f.write("WARC/1.0\n")

            # Write all WARC headers
            f.write(f"WARC-Type: {record.record.record_type}\n")
            f.write(f"WARC-Record-ID: {record.record.record_id}\n")
            f.write(f"WARC-Date: {record.record.date_str}\n")
            f.write(f"WARC-Target-URI: {record.record.target_uri}\n")
            f.write(f"Content-Type: {record.record.content_type}\n")

            # Write payload digest if present
            if record.record.payload_digest:
                f.write(
                    f"WARC-Payload-Digest: {record.record.payload_digest}\n")

            # Write any additional headers from the original record
            for key, value in record.record.headers.items():
                # Skip headers we've already written
                if not key.lower() in [
                        'warc-type', 'warc-record-id', 'warc-date',
                        'warc-target-uri', 'content-type', 'warc-payload-digest'
                ]:
                    f.write(f"{key}: {value}\n")

            # Add content length header for the processed content
            content_length = len(record.processed_content.encode('utf-8'))
            f.write(f"Content-Length: {content_length}\n")

            # Add blank line before content as per WARC spec
            f.write("\n")

            # Write the processed plaintext content
            f.write(record.processed_content)

            # Add record delimiter as per WARC spec
            f.write("\n\nWARC/1.0\n\n")
