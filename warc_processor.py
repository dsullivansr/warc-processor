"""WARC file processor.

This module provides functionality for processing WARC files.
"""

import logging
from typing import List

from warcio.archiveiterator import ArchiveIterator

from models.warc_record import ProcessedWarcRecord
from output_writer import OutputWriter
from processing_stats import ProcessingStats
from warc_record_parser import WarcRecordParser
from warc_record_processor import WarcRecordProcessor
from warc_record_processor_chain import WarcRecordProcessorChain

logger = logging.getLogger(__name__)


class WarcProcessor:
    """Processes WARC files.

    Responsibilities:
    1. Reading WARC records
    2. Parsing records into domain objects
    3. Processing records through processor chain
    4. Writing processed records
    5. Tracking processing statistics
    """

    # TODO(dsullivan): Consider refactoring to reduce constructor arguments by
    # having WarcProcessor create its own processor_chain from processors.
    # pylint: disable=too-many-arguments
    def __init__(self, *, processors: List[WarcRecordProcessor],
                 output_writer: OutputWriter, record_parser: WarcRecordParser,
                 stats: ProcessingStats,
                 processor_chain: WarcRecordProcessorChain):
        """Initialize processor.

        Args:
            processors: List of record processors
            output_writer: Writer for processed records
            record_parser: Parser for WARC records
            stats: Stats tracker
            processor_chain: Chain of processors
        """
        self.processors = processors
        self.output_writer = output_writer
        self.record_parser = record_parser
        self.stats = stats
        self.processor_chain = processor_chain

    def process_warc_file(self, warc_path: str,
                          output_path: str) -> ProcessingStats:
        """Process a WARC file.

        Reads records from the WARC file, processes them through the processor
        chain, and writes results to the output file.

        Args:
            warc_path: Path to input WARC file
            output_path: Path to output file

        Returns:
            Processing statistics

        Raises:
            IOError: If input file can't be read or output file can't be written
            ValueError: If WARC file is invalid
        """
        # Configure output writer
        self.output_writer.configure(output_path)

        # Initialize stats
        self.stats.start_processing(warc_path)

        try:
            # Process records
            with open(warc_path, 'rb') as warc_file:
                for record in ArchiveIterator(warc_file):
                    # Track bytes processed
                    try:
                        content_length = int(
                            record.http_headers.get('Content-Length', 0))
                    except (ValueError, AttributeError, TypeError):
                        content_length = 0

                    self.stats.track_bytes_processed(content_length)

                    # Parse record
                    warc_record = self.record_parser.parse(record)
                    if not warc_record:
                        continue

                    # Track parsed record
                    self.stats.track_parsed_record()

                    # Process record
                    processed_content = self.processor_chain.process(
                        warc_record)
                    if not processed_content:
                        self.stats.track_skipped_record()
                        continue

                    # Write processed record
                    processed_record = ProcessedWarcRecord.from_record(
                        warc_record, processed_content)
                    self.output_writer.write_record(processed_record)

                    # Track processed record
                    self.stats.track_processed_record()

        except FileNotFoundError:
            logger.error("WARC file not found: %s", warc_path)
            raise

        except (IOError, OSError) as e:
            logger.error("Failed to process WARC file: %s", str(e))
            raise

        finally:
            # Finish processing
            self.stats.finish_processing()

        return self.stats
