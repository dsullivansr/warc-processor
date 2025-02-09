"""Factory for creating WarcProcessor instances."""

import logging
import os
import yaml
from typing import List, Optional

from processors.lexbor_html_processor import LexborHtmlProcessor
from processing_stats import ProcessingStats
from warc_processor import WarcProcessor
from warc_record_parser import WarcRecordParser
from warc_record_processor import WarcRecordProcessor
from writers.plain_text_writer import PlainTextWriter

logger = logging.getLogger(__name__)


class WarcProcessorFactory:
    """Factory for creating WarcProcessor instances."""

    @staticmethod
    def create(
        *,
        processors: Optional[List[WarcRecordProcessor]] = None,
        record_parser: Optional[WarcRecordParser] = None,
        output_writer: Optional[PlainTextWriter] = None,
        stats: Optional[ProcessingStats] = None
    ) -> WarcProcessor:
        """Create a WarcProcessor instance with optional custom components.

        Args:
            processors: List of WarcRecordProcessor instances (default: empty list)
            record_parser: Optional custom WarcRecordParser (default: WarcRecordParser())
            output_writer: Optional custom OutputWriter (default: PlainTextWriter())
            stats: Optional custom ProcessingStats instance (default: ProcessingStats())

        Returns:
            Configured WarcProcessor instance
        """
        if not processors:
            processors = [LexborHtmlProcessor()]
        if record_parser is None:
            record_parser = WarcRecordParser()
        if output_writer is None:
            output_writer = PlainTextWriter()
        if stats is None:
            stats = ProcessingStats()
        return WarcProcessor(
            record_parser=record_parser,
            processors=processors,
            output_writer=output_writer,
            stats=stats,
        )
