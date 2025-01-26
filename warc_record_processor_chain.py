"""Chain of WARC record processors.

This module provides functionality for chaining multiple WARC record processors.
"""

import logging
from typing import List, Optional
from bs4.builder import ParserRejectedMarkup
from models.warc_record import WarcRecord
from warc_record_processor import WarcRecordProcessor

logger = logging.getLogger(__name__)


class WarcRecordProcessorChain:
    """Chain of WARC record processors.

    Attributes:
        processors: List of processors to apply in sequence
    """

    def __init__(self, processors: List[WarcRecordProcessor]):
        """Initialize processor chain.

        Args:
            processors: List of processors to apply in sequence
        """
        self.processors = processors

    def process(self, record: WarcRecord) -> Optional[str]:
        """Process a WARC record through the chain of processors.

        Each processor in the chain is applied in sequence. If any processor
        returns None, the chain is stopped and None is returned.

        Args:
            record: WARC record to process

        Returns:
            Processed content or None if record should be skipped
        """
        if not record.content:
            return None

        # Track if any processor handled the record
        processed = False

        # Apply each processor in sequence
        content = record.content
        for processor in self.processors:
            # Check if processor can handle record
            if not processor.can_process(record):
                continue

            try:
                # Process record
                result = processor.process(record)

                # Update content for next processor
                if result is not None:
                    content = result
                    processed = True

            except (ValueError, ParserRejectedMarkup, UnicodeDecodeError) as e:
                logger.error("Processor %s failed: %s",
                             processor.__class__.__name__, str(e))
                return None

        # Return None if no processor succeeded
        return content if processed else None
