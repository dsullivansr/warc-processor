import importlib
import logging
import os

from typing import Any, Dict, List


class WarcProcessorFactory:
    """Factory class for creating WARC processors."""

    def __init__(self) -> None:
        self.processors: Dict[str, Any] = {}

    def create(self, processor_config: Dict[str, Any]) -> Any:
        """
        Creates a processor based on the given configuration.
        """
        logging.debug("Creating processor: %s", processor_config)

        # Load the module
        try:
            module_name = processor_config["class"].split(".")[0]
            module = importlib.import_module(module_name)
        except ImportError as e:
            logging.error("Could not import module %s: %s", module_name, e)
            raise

        # Load the class
        processor_class = getattr(module, processor_config["class"], None)
        if processor_class is None:
            raise AttributeError(
                f"Module '{module_name}' has no attribute '{processor_config['class']}'"
            )

        if "config" in processor_config:
            config = processor_config["config"]
            processor = processor_class(**config)
        else:
            processor = processor_class()

        return processor

    def get_available_processors(self, directory: str) -> List[str]:
        """Gets all available processors in the given directory."""
        processors_list: List[str] = []
        for filename in os.listdir(directory):
            if filename.endswith(".py") and filename != "__init__.py":
                processors_list.append(filename[:-3])

        logging.debug("Available processors: %s", processors_list)
        return processors_list
