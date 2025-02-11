from warc_processor import WarcProcessor
from warc_record_parser import WarcRecordParser
from processing_stats import ProcessingStats
from writers.plain_text_writer import PlainTextWriter
from writers.json_writer import JsonWriter
from processors.lexbor_html_processor import LexborHtmlProcessor
from processors.beautiful_soup_html_processor import BeautifulSoupHtmlProcessor
from warc_processor_types import OutputWriters, RecordProcessors


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
        record_parser=None,
        stats=None
    ) -> WarcProcessor:
        """Creates a WarcProcessor with specified configuration.

        Args:
            processors: List of record processors or RecordProcessors enum.
                Defaults to RecordProcessors.LEXBOR.
            output_writer: Output writer instance or OutputWriters enum.
                Defaults to OutputWriters.PLAIN_TEXT.
            record_parser: Optional record parser instance.
            stats: Optional stats instance.
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

        parser = record_parser or WarcRecordParser()
        stats_instance = stats or ProcessingStats()

        return WarcProcessor(
            processor=processor,
            output_writer=writer,
            record_parser=parser,
            stats=stats_instance
        )
