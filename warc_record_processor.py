"""WARC record processor interface.

This module defines the interface for processors that can transform WARC records
into processed content.
"""

from abc import ABC, abstractmethod

from models.warc_record import WarcRecord


class WarcRecordProcessor(ABC):
    """Interface for processors that can transform WARC records.
    
    Processors implementing this interface are responsible for:
    1. Determining if they can handle a given record type
    2. Transforming the record content into a processed form
    3. Handling any errors that occur during processing
    """
    
    @abstractmethod
    def can_process(self, record: WarcRecord) -> bool:
        """Check if this processor can handle the given record.
        
        Args:
            record: WARC record to check.
            
        Returns:
            True if this processor can handle the record, False otherwise.
        """
        pass
        
    @abstractmethod
    def process(self, record: WarcRecord) -> str:
        """Process a WARC record.
        
        Args:
            record: WARC record to process.
            
        Returns:
            Processed content as a string.
            
        Raises:
            ValueError: If record cannot be processed.
        """
        pass
