import logging
from typing import Any, Dict, List, Optional

from warc_processor import WarcProcessor
from warc_record_processor import WarcRecordProcessor
from warc_record_parser import WarcRecordParser
from output_writer import OutputWriter
from processing_stats import ProcessingStats
from writers.plain_text_writer import PlainTextWriter


class WarcProcessorFactory:
    """Factory class for creating WARC processors with default configuration.
    
    This factory creates a WarcProcessor instance with default settings,
    ensuring compatibility with PyInstaller by avoiding dynamic imports.
    """

    def create(
        self, processor_config: Optional[Dict[str, Any]] = None
    ) -> WarcProcessor:
        """Creates a WarcProcessor with default configuration.

        Args:
            processor_config: Optional configuration dictionary. If provided,
                will be used instead of defaults.
        """
        if processor_config is None:
            # Create default components
            processors: List[WarcRecordProcessor] = []
            output_writer: OutputWriter = PlainTextWriter()
            record_parser = WarcRecordParser()
            stats = ProcessingStats()

            # Create WarcProcessor with default settings
            return WarcProcessor(
                processors=processors,
                output_writer=output_writer,
                record_parser=record_parser,
                stats=stats
            )

        logging.debug("Creating processor with config: %s", processor_config)
        return WarcProcessor(**processor_config)
