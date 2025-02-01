"""Dynamic processor loader."""

import importlib
import inspect
import logging
import os
from typing import List

import yaml

from warc_record_processor import WarcRecordProcessor

logger = logging.getLogger(__name__)


class ProcessorLoader:
    """Dynamically loads processors from the processors directory."""

    @staticmethod
    def _get_processor_classes(processor_dir: str) -> dict:
        """Get processor classes from directory.

        Args:
            processor_dir: Directory containing processor modules

        Returns:
            Dictionary mapping class names to processor classes
        """
        processor_files = [
            f[:-3]
            for f in os.listdir(processor_dir)
            if f.endswith('.py') and not f.startswith('__')
        ]

        processor_classes = {}
        for module_name in processor_files:
            module = importlib.import_module(f'processors.{module_name}')
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, WarcRecordProcessor) and
                        obj != WarcRecordProcessor):
                    processor_classes[name] = obj

        return processor_classes

    @staticmethod
    def load_processors(config_path: str,
                        **overrides) -> List[WarcRecordProcessor]:
        """Load processors based on configuration.

        Args:
            config_path: Path to YAML configuration file
            **overrides: Configuration overrides from command line

        Returns:
            List of instantiated processor objects

        Raises:
            ValueError: If processor class cannot be found or instantiated
        """
        # Load configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        processor_dir = os.path.join(os.path.dirname(__file__), 'processors')
        processor_classes = ProcessorLoader._get_processor_classes(
            processor_dir)

        # Instantiate configured processors
        processors = []
        for processor_config in config.get('processors', []):
            class_name = processor_config['class']
            if class_name not in processor_classes:
                msg = (f'Processor class {class_name} not found in '
                       'processors directory')
                raise ValueError(msg)

            # Merge config with overrides
            merged_config = processor_config.get('config', {})
            merged_config.update(overrides)

            try:
                processor = processor_classes[class_name](**merged_config)
                processors.append(processor)
            except Exception as e:
                raise ValueError(
                    f'Failed to instantiate processor {class_name}: '
                    f'{str(e)}') from e

        return processors
