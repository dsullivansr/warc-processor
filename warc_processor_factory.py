"""Factory for creating WarcProcessor instances."""

import logging
import os
import yaml
from typing import List, Optional

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
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        # Dynamic processor loading removed; processors configuration is no longer supported.
        return WarcProcessorFactory.create([])

    @staticmethod
    def create(
        processors: Optional[List[WarcRecordProcessor]] = None,
    ) -> WarcProcessor:
        """Create a WarcProcessor instance.

        Args:
            processors: List of WarcRecordProcessor instances

        Returns:
            WarcProcessor instance
        """
        if processors is None:
            processors = []

        return WarcProcessor(
            record_parser=WarcRecordParser(),
            processors=processors,
            output_writer=PlainTextWriter(),
            stats=ProcessingStats(),
        )
