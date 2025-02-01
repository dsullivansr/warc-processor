"""Factory for creating WarcProcessor instances."""

import logging
import os
from typing import List, Optional

import yaml

from component_loader import ComponentLoader
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

        Raises:
            ValueError: If processor class cannot be found or instantiated
        """
        # Load configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Load processor classes
        processor_dir = os.path.join(os.path.dirname(__file__), 'processors')
        processor_classes = ComponentLoader.load_components(
            processor_dir,
            WarcRecordProcessor,
        )

        # Instantiate configured processors
        processors = []
        for processor_config in config.get('processors', []):
            class_name = processor_config['class']
            if class_name not in processor_classes:
                msg = (f'Processor class {class_name} not found in '
                       'processors dir')
                raise ValueError(msg)

            # Merge config with overrides
            merged_config = processor_config.get('config', {})
            merged_config.update(overrides)

            try:
                processor = processor_classes[class_name](**merged_config)
                processors.append(processor)
            except Exception as e:
                msg = (f'Failed to instantiate processor {class_name}: '
                       f'{str(e)}')
                raise ValueError(msg) from e

        return WarcProcessorFactory.create(processors)

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
