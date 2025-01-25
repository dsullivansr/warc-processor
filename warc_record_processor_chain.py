"""WARC record processor chain.

This module provides functionality for chaining multiple record processors
together.
"""

import logging
from typing import List, Optional

from models.warc_record import WarcRecord
from warc_record_processor import WarcRecordProcessor

logger = logging.getLogger(__name__)


class WarcRecordProcessorChain:
    """Chain of WARC record processors.
    
    This class coordinates the application of multiple processors to a record by:
    1. Applying processors in sequence
    2. Handling processor failures
    3. Aggregating processor results
    """
    
    def __init__(self, processors: List[WarcRecordProcessor]):
        """Initialize processor chain.
        
        Args:
            processors: List of processors to apply to records.
        """
        self.processors = processors
        
    def process(self, record: WarcRecord) -> Optional[str]:
        """Process a record through the chain.
        
        Applies each processor in sequence. If any processor fails or skips the
        record, stops processing and returns None.
        
        Args:
            record: WARC record to process.
            
        Returns:
            Processed content as string if successful, None if skipped.
            
        Raises:
            ValueError: If processing fails.
        """
        # Process record through chain
        current_content = None
        for processor in self.processors:
            # Check if processor can handle record
            if not processor.can_process(record):
                continue
                
            try:
                result = processor.process(record)
                if result is not None:
                    # Update content for next processor
                    current_content = result
                    record.content = current_content
                    
            except Exception as e:
                logger.error("Processor %s failed: %s",
                           processor.__class__.__name__, str(e))
                return None
                    
        # Return None if no processor succeeded
        if not current_content:
            return None
            
        return current_content
