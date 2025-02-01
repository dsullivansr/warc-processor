"""Factory for creating WarcProcessor instances."""

import logging
from typing import List, Optional

from processor_loader import ProcessorLoader
from processing_stats import ProcessingStats
from warc_processor import WarcProcessor
from warc_record_parser import WarcRecordParser
from warc_record_processor import WarcRecordProcessor
from writers.plain_text_writer import PlainTextWriter

logger = logging.getLogger(__name__)


class WarcProcessorFactory:
    """Factory for creating WarcProcessor instances."""

    @staticmethod
    def create_from_config(config_path: str, **overrides) -> WarcProcessor:
        """Create a WarcProcessor instance from configuration.

        Args:
            config_path: Path to YAML configuration file
            **overrides: Configuration overrides from command line

        Returns:
            Configured WarcProcessor instance
        """
        try:
            processors = ProcessorLoader.load_processors(
                config_path, **overrides)
            return WarcProcessorFactory.create(processors)
        except Exception as e:
            logger.error("Failed to create processor from config: %s", str(e))
            raise

    @staticmethod
    def create(
        processors: Optional[List[WarcRecordProcessor]] = None
    ) -> WarcProcessor:
        """Create a WarcProcessor instance.

        Args:
            processors: List of WarcRecordProcessor instances

        Returns:
            WarcProcessor instance
        """
        if processors is None:
            processors = []

        output_writer = PlainTextWriter()
        record_parser = WarcRecordParser()
        stats = ProcessingStats()

        return WarcProcessor(processors=processors,
                             output_writer=output_writer,
                             record_parser=record_parser,
                             stats=stats)
