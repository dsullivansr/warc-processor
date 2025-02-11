from warc_processor import WarcProcessor
from warc_record_parser import WarcRecordParser
from processing_stats import ProcessingStats
from writers.plain_text_writer import PlainTextWriter
from writers.json_writer import JsonWriter
from processors.lexbor_html_processor import LexborHtmlProcessor
from processors.beautiful_soup_html_processor import BeautifulSoupHtmlProcessor
from warc_processor_types import (
    OutputWriters,
    RecordProcessors,
    RecordParsers,
    ProcessingStats as StatsTypes
)


class WarcProcessorFactory:
    """Factory class for creating WARC processors with default configuration.
    
    This factory creates a WarcProcessor instance with default settings,
    ensuring compatibility with PyInstaller by avoiding dynamic imports.
    """

    def create(
        self,
        *,
        processors: RecordProcessors = RecordProcessors.DEFAULT,
        output_writer: OutputWriters = OutputWriters.DEFAULT,
        record_parser: RecordParsers = RecordParsers.DEFAULT,
        stats: StatsTypes = StatsTypes.DEFAULT
    ) -> WarcProcessor:
        """Creates a WarcProcessor with specified configuration.

        Args:
            processors: List of record processors or RecordProcessors enum.
                Defaults to RecordProcessors.LEXBOR.
            output_writer: Output writer instance or OutputWriters enum.
                Defaults to OutputWriters.PLAIN_TEXT.
            record_parser: Record parser instance or RecordParsers enum.
                Defaults to RecordParsers.DEFAULT.
            stats: Processing stats instance or StatsTypes enum.
                Defaults to StatsTypes.DEFAULT.
        """
        # Create processor from enum
        if processors in (RecordProcessors.DEFAULT, RecordProcessors.LEXBOR):
            processor = LexborHtmlProcessor()
        elif processors == RecordProcessors.BEAUTIFUL_SOUP_LXML:
            processor = BeautifulSoupHtmlProcessor(parser='lxml')
        elif processors == RecordProcessors.BEAUTIFUL_SOUP_HTML5:
            processor = BeautifulSoupHtmlProcessor(parser='html5lib')
        elif processors == RecordProcessors.BEAUTIFUL_SOUP_BUILTIN:
            processor = BeautifulSoupHtmlProcessor(parser='html.parser')
        else:
            raise ValueError(f"Unknown processor type: {processors}")

        if output_writer in (OutputWriters.DEFAULT, OutputWriters.TEXT):
            writer = PlainTextWriter()
        elif output_writer == OutputWriters.JSON:
            writer = JsonWriter()
        else:
            raise ValueError(f"Unknown writer type: {output_writer}")

        if record_parser == RecordParsers.DEFAULT:
            parser = WarcRecordParser()
        else:
            raise ValueError(f"Unknown parser type: {record_parser}")

        if stats == StatsTypes.DEFAULT:
            stats_instance = ProcessingStats()
        else:
            raise ValueError(f"Unknown stats type: {stats}")

        return WarcProcessor(
            processor=processor,
            output_writer=writer,
            record_parser=parser,
            stats=stats_instance
        )
