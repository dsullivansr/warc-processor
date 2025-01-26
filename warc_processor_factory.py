"""Factory for creating WARC processors."""

from typing import List

from html_processor import HtmlProcessor
from plain_text_writer import PlainTextWriter
from processing_stats import ProcessingStats
from warc_processor import WarcProcessor
from warc_record_parser import WarcRecordParser
from warc_record_processor import WarcRecordProcessor
from warc_record_processor_chain import WarcRecordProcessorChain


class WarcProcessorFactory:
    """Factory for creating WARC processors with standard components."""

    @staticmethod
    def create(processors: List[WarcRecordProcessor] = None) -> WarcProcessor:
        """Create a new WARC processor with default components.

        Args:
            processors: List of processors to use, defaults to [HtmlProcessor()]

        Returns:
            Configured WarcProcessor instance.
        """
        if not processors:
            processors = [HtmlProcessor()]

        # Create all required components
        processor_chain = WarcRecordProcessorChain(processors)
        record_parser = WarcRecordParser()
        stats = ProcessingStats()
        output_writer = PlainTextWriter()

        # Create and return processor
        return WarcProcessor(processors=processors,
                             output_writer=output_writer,
                             record_parser=record_parser,
                             stats=stats,
                             processor_chain=processor_chain)
