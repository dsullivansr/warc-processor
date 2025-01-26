"""WARC file processor.

This module provides functionality for coordinating the processing of WARC files.
"""

import logging
from typing import List

from warcio.archiveiterator import ArchiveIterator

from models.warc_paths import OutputPath, WarcPath
from models.warc_record import ProcessedWarcRecord
from output_writer import OutputWriter
from processing_stats import ProcessingStats
from warc_record_parser import WarcRecordParser
from warc_record_processor import WarcRecordProcessor
from warc_record_processor_chain import WarcRecordProcessorChain

logger = logging.getLogger(__name__)


class WarcProcessor:
    """Processes WARC files by applying a chain of record processors.

    This class coordinates the processing of WARC files by:
    1. Reading and parsing WARC records
    2. Applying a chain of processors to each record
    3. Writing processed records to output
    4. Tracking processing statistics
    """

    def __init__(
            self,
            processors: List[WarcRecordProcessor],
            output_writer: OutputWriter,
            record_parser: WarcRecordParser,
            stats: ProcessingStats,
            processor_chain: WarcRecordProcessorChain
    ):
        """Initialize processor.

        Args:
            processors: List of record processors to apply to each record.
            output_writer: Writer for storing processed records.
            record_parser: Parser for reading WARC records.
            stats: Object for tracking processing statistics.
            processor_chain: Chain for coordinating processors.
        """
        self.processors = processors
        self.output_writer = output_writer
        self.record_parser = record_parser
        self.stats = stats
        self.processor_chain = processor_chain

    def process_warc_file(
            self,
            warc_path: str,
            output_path: str
    ) -> ProcessingStats:
        """Process a WARC file.

        Reads records from the WARC file, processes them through the processor
        chain, and writes results to the output file.

        Args:
            warc_path: Path to input WARC file.
            output_path: Path for output file.

        Returns:
            Statistics about the processing run.

        Raises:
            FileNotFoundError: If WARC file does not exist.
            PermissionError: If output path is not writable.
            ValueError: If processor chain fails.
        """
        # Validate and normalize paths
        input_path = WarcPath(warc_path)
        output = OutputPath(output_path)

        # Configure output writer
        self.output_writer.configure(str(output))

        # Set input size
        self.stats.set_input_size(str(input_path))

        print(f"\nProcessing WARC file: {input_path}")
        print(f"File size: {self.stats.input_size_mb:.1f} MB")
        print("-" * 50)

        # Process records
        bytes_processed = 0
        with open(str(input_path), 'rb') as warc_file:
            for record in ArchiveIterator(warc_file):
                try:
                    # Update bytes processed by reading content length
                    content_length = 0
                    if record.http_headers:
                        content_length = int(
                            record.http_headers.get('Content-Length', 0))
                    bytes_processed += content_length
                    self.stats.track_bytes_processed(bytes_processed)
                    
                    # Parse record
                    warc_record = self.record_parser.parse(record)
                    if not warc_record:
                        # Skip non-response records without tracking
                        continue

                    self.stats.track_parsed_record()

                    # Process record
                    processed_content = self.processor_chain.process(warc_record)
                    if not processed_content:
                        self.stats.track_skipped_record()
                        continue

                    # Create processed record and write
                    processed_record = ProcessedWarcRecord.from_record(
                        warc_record,
                        processed_content
                    )
                    self.output_writer.write_record(processed_record)
                    self.stats.track_processed_record()

                except Exception as e:
                    logger.error("Failed to process record: %s", str(e))
                    self.stats.track_failed_record()

        return self.stats
