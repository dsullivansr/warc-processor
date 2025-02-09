"""Process WARC files."""

import logging
from typing import List, Optional

from warcio.archiveiterator import ArchiveIterator

from models.warc_record import ProcessedWarcRecord, WarcRecord
from output_writer import OutputWriter
from processing_stats import ProcessingStats
from warc_record_parser import WarcRecordParser
from warc_record_processor import ProcessorInput, WarcRecordProcessor

logger = logging.getLogger(__name__)


class WarcProcessor:
    """Process WARC files."""

    def __init__(
        self,
        processors: List[WarcRecordProcessor],
        output_writer: OutputWriter,
        record_parser: WarcRecordParser,
        stats: ProcessingStats,
    ):
        """Initialize the processor.

        Args:
            processors: List of record processors to use
            output_writer: Writer for processed records
            record_parser: Parser for WARC records
            stats: Processing statistics tracker
        """
        self.processors = processors
        self.output_writer = output_writer
        self.record_parser = record_parser
        self.stats = stats

    def process_warc_file(
        self, input_path: str, output_path: str
    ) -> ProcessingStats:
        """Process a WARC file.

        Args:
            input_path: Path to input WARC file
            output_path: Path to output file

        Returns:
            Processing statistics
        """
        if not input_path:
            logger.error("No input file provided")
            return self.stats

        try:
            self.output_writer.configure(output_path)
            self.stats.start_processing(input_path)
            self._process_records_from_file(input_path)
        except (IOError, OSError) as e:
            logger.error("Failed to process WARC file: %s", str(e))
            raise

        self.stats.finish_processing()
        return self.stats

    def _process_records_from_file(self, input_path: str) -> None:
        """Process all records from a WARC file.

        Args:
            input_path: Path to input WARC file
        """
        with open(input_path, "rb") as warc_file:
            for record in ArchiveIterator(warc_file):
                self._process_single_record(record)

    def _process_single_record(self, record) -> None:
        """Process a single record from the WARC file.

        Args:
            record: Raw WARC record to process
        """
        try:
            parsed_record = self.record_parser.parse(record)
            self.stats.track_parsed_record()

            processed_content = self._process_record(parsed_record)
            if processed_content:
                processed_record = ProcessedWarcRecord(
                    record=parsed_record, processed_content=processed_content
                )
                self.output_writer.write_record(processed_record)
                self.stats.track_processed_record()
            else:
                self.stats.track_skipped_record()
        except (ValueError, AttributeError) as e:
            logger.error("Failed to process record: %s", str(e))
            self.stats.track_skipped_record()

    def _process_record(self, record: WarcRecord) -> Optional[str]:
        """Process a single WARC record.

        Args:
            record: WARC record to process

        Returns:
            Processed text content or None if processing failed
        """
        if not record.content or not record.content_type:
            return None

        # Track bytes processed even if processing fails
        if record.content:
            self.stats.track_bytes_processed(len(record.content))

        try:
            # Try each processor in turn
            for processor in self.processors:
                if processor.can_process(record.content_type):
                    processor_input = ProcessorInput(
                        content=record.content, content_type=record.content_type
                    )
                    return processor.process(processor_input)
        except (ValueError, AttributeError) as e:
            logger.error(
                "Failed to process record %s: %s", record.record_id, str(e)
            )
            return None

        return None
