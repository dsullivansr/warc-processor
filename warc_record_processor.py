"""WARC record processor interface.

This module defines the interface for processors that can transform content
from WARC records into processed form.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from models.warc_mime_types import ContentType


@dataclass
class ProcessorInput:
    """Input for content processing.

    Attributes:
        content: Raw content to process
        content_type: Type of the content
    """

    content: str
    content_type: ContentType


class WarcRecordProcessor(ABC):
    """Interface for processors that can transform content.

    Processors implementing this interface are responsible for:
    1. Determining if they can handle a given content type
    2. Transforming the content into a processed form
    3. Handling any errors that occur during processing
    """

    @abstractmethod
    def can_process(self, processor_input: ProcessorInput) -> bool:
        """Check if this processor can handle the input.

        This method determines whether the processor should handle the given input.
        It can make this decision based on any aspect of the input, such as:
        - Content type
        - Content characteristics
        - Content length
        - Previous processing results
        - etc.

        Args:
            processor_input: Input to potentially process

        Returns:
            True if this processor should handle the input, False to skip it.
        """

    @abstractmethod
    def process(self, processor_input: ProcessorInput) -> str:
        """Process content.

        Args:
            processor_input: Input to process

        Returns:
            Processed content as a string.

        Raises:
            ValueError: If content cannot be processed.
        """
