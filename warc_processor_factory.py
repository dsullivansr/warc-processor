import logging
from typing import Any, Dict, List, Optional

from warc_processor import WarcProcessor
from warc_record_processor import WarcRecordProcessor
from warc_record_parser import WarcRecordParser
from output_writer import OutputWriter
from processing_stats import ProcessingStats
from writers.plain_text_writer import PlainTextWriter
from processors.beautiful_soup_html_processor import BeautifulSoupHtmlProcessor
from processors.lexbor_html_processor import LexborHtmlProcessor


class WarcProcessorFactory:
    """Factory class for creating WARC processors with default configuration.
    
    This factory creates a WarcProcessor instance with default settings,
    ensuring compatibility with PyInstaller by avoiding dynamic imports.
    """

    def create(
        self,
        *,
        processors: Optional[List[WarcRecordProcessor]] = None,
        output_writer: Optional[OutputWriter] = None,
        record_parser: Optional[WarcRecordParser] = None,
        stats: Optional[ProcessingStats] = None,
        processor_type: Optional[str] = None
    ) -> WarcProcessor:
        """Creates a WarcProcessor with default configuration.

        Args:
            processors: Optional list of record processors. If not provided, will be determined by processor_type.
            output_writer: Optional output writer. If not provided, uses PlainTextWriter.
            record_parser: Optional record parser. If not provided, uses WarcRecordParser.
            stats: Optional processing stats. If not provided, uses ProcessingStats.
            processor_type: Optional processor type ('BeautifulSoupHtmlProcessor' or 'LexborHtmlProcessor').
                If provided, will be used to create the processor list.
        """
        # Create processor list based on type if not provided
        if processors is None:
            if processor_type == "BeautifulSoupHtmlProcessor":
                processors = [BeautifulSoupHtmlProcessor()]
            elif processor_type == "LexborHtmlProcessor":
                processors = [LexborHtmlProcessor()]
            else:
                processors = []

        # Use defaults for other components if not provided
        if output_writer is None:
            output_writer = PlainTextWriter()
        if record_parser is None:
            record_parser = WarcRecordParser()
        if stats is None:
            stats = ProcessingStats()

        return WarcProcessor(
            processors=processors,
            output_writer=output_writer,
            record_parser=record_parser,
            stats=stats
        )
