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
    def can_process(self, content_type: ContentType) -> bool:
        """Check if this processor can handle the content type.
        
        Args:
            content_type: Type of content to check.
            
        Returns:
            True if this processor can handle the content type, False otherwise.
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
