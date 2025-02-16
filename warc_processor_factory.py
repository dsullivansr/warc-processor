from models.component_types import OutputWriters, RecordProcessors
from processing_stats import ProcessingStats
from processors.beautiful_soup_html_processor import BeautifulSoupHtmlProcessor
from processors.lexbor_html_processor import LexborHtmlProcessor
from warc_processor import WarcProcessor
from warc_record_parser import WarcRecordParser
from writers.json_writer import JsonWriter
from writers.plain_text_writer import PlainTextWriter


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
    ) -> WarcProcessor:
        """Creates a WarcProcessor with specified configuration.

        Args:
            processors: List of record processors or RecordProcessors enum.
                Defaults to RecordProcessors.LEXBOR.
            output_writer: Output writer instance or OutputWriters enum.
                Defaults to OutputWriters.PLAIN_TEXT.

        """
        # Create processors from enum or list
        processor_list = []

        if isinstance(processors, (list, tuple)):
            # Handle list of processor instances
            processor_list.extend(processors)
        else:
            # Create processor from enum
            if processors in (RecordProcessors.DEFAULT, RecordProcessors.LEXBOR):
                processor_list.append(LexborHtmlProcessor())
            elif processors == RecordProcessors.BEAUTIFUL_SOUP_LXML:
                processor_list.append(BeautifulSoupHtmlProcessor(parser="lxml"))
            elif processors == RecordProcessors.BEAUTIFUL_SOUP_HTML5:
                processor_list.append(BeautifulSoupHtmlProcessor(parser="html5lib"))
            elif processors == RecordProcessors.BEAUTIFUL_SOUP_BUILTIN:
                processor_list.append(BeautifulSoupHtmlProcessor(parser="html.parser"))
            else:
                raise ValueError(f"Unknown processor type: {processors}")

        if output_writer in (OutputWriters.DEFAULT, OutputWriters.TEXT):
            writer = PlainTextWriter()
        elif output_writer == OutputWriters.JSON:
            writer = JsonWriter()
        else:
            raise ValueError(f"Unknown writer type: {output_writer}")

        parser = WarcRecordParser()
        stats_instance = ProcessingStats()

        return WarcProcessor(
            processors=processor_list,
            output_writer=writer,
            record_parser=parser,
            stats=stats_instance,
        )
