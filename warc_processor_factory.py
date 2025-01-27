"""Factory for creating WARC processors."""

from typing import List, Optional

from beautiful_soup_html_processor import BeautifulSoupHtmlProcessor
from output_writer import OutputWriter
from plain_text_writer import PlainTextWriter
from processing_stats import ProcessingStats
from warc_processor import WarcProcessor
from warc_record_parser import WarcRecordParser
from warc_record_processor import WarcRecordProcessor
from warc_record_processor_chain import WarcRecordProcessorChain


class WarcProcessorFactory:
    """Factory for creating WARC processors.

    This factory provides methods for creating and configuring WARC processors
    with different record processors and output writers.
    """

    @staticmethod
    def create(processors: Optional[List[WarcRecordProcessor]] = None,
               output_writer: Optional[OutputWriter] = None) -> WarcProcessor:
        """Create a new WARC processor with default components.

        Args:
            processors: List of processors to use
            output_writer: Optional writer to use

        Returns:
            Configured WarcProcessor instance.
        """
        if not processors:
            processors = [BeautifulSoupHtmlProcessor()]

        # Create all required components
        processor_chain = WarcRecordProcessorChain(processors)
        record_parser = WarcRecordParser()
        stats = ProcessingStats()
        if output_writer is None:
            output_writer = PlainTextWriter()

        # Create and return processor
        return WarcProcessor(processors=processors,
                             output_writer=output_writer,
                             record_parser=record_parser,
                             stats=stats,
                             processor_chain=processor_chain)
