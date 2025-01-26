"""Plain text writer implementation.

This module provides a concrete implementation of the OutputWriter interface
that writes processed WARC records to a plain text file in a simple format.
"""

import logging
import os

from models.warc_record import ProcessedWarcRecord
from output_writer import OutputWriter

logger = logging.getLogger(__name__)


class PlainTextWriter(OutputWriter):
    """Writes processed records to a plain text file.
    
    This writer creates a text file containing the processed WARC records, with
    each record's metadata and content separated by newlines. The format is:
    
    WARC-Target-URI: [uri]
    WARC-Date: [date]
    Content-Type: [type]
    
    [processed content]
    
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
            f.write(f"WARC-Target-URI: {record.record.target_uri}\n")
            f.write(f"WARC-Date: {record.record.date_str}\n")
            f.write(f"Content-Type: {record.record.content_type}\n")
            f.write("\n")
            f.write(record.processed_content)
            f.write("\n\n")
