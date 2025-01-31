"""Factory for creating WARC processors."""

from beautiful_soup_html_processor import BeautifulSoupHtmlProcessor
from processors.lexbor_html_processor import LexborHtmlProcessor
from processing_stats import ProcessingStats
from plain_text_writer import PlainTextWriter
from warc_processor import WarcProcessor
from warc_record_parser import WarcRecordParser


class WarcProcessorFactory:
    """Factory for creating WarcProcessor instances."""

    @staticmethod
    def create(processors=None, output_writer=None) -> WarcProcessor:
        """Create a new WARC processor with default components.

        Args:
            processors: List of record processors to use
            output_writer: Output writer to use

        Returns:
            WarcProcessor instance
        """
        if processors is None:
            processors = [BeautifulSoupHtmlProcessor()]

        # Create all required components
        record_parser = WarcRecordParser()
        stats = ProcessingStats()
        if output_writer is None:
            output_writer = PlainTextWriter()

        return WarcProcessor(processors=processors,
                             output_writer=output_writer,
                             record_parser=record_parser,
                             stats=stats)

    def create_processor(self) -> WarcProcessor:
        """Create a new WarcProcessor instance.

        Returns:
            WarcProcessor instance
        """
        output_writer = PlainTextWriter()
        record_parser = WarcRecordParser()
        stats = ProcessingStats()

        return WarcProcessor(
            processors=[BeautifulSoupHtmlProcessor(),
                        LexborHtmlProcessor()],
            output_writer=output_writer,
            record_parser=record_parser,
            stats=stats)
