"""HTML processor for WARC records.

This module provides functionality for processing HTML content from WARC records,
extracting readable text while removing markup and unwanted elements.
"""

import logging
import re
from typing import Optional

from bs4 import BeautifulSoup

from models.warc_record import WarcRecord, ProcessedWarcRecord
from warc_record_processor import WarcRecordProcessor

logger = logging.getLogger(__name__)


class HtmlProcessor(WarcRecordProcessor):
    """Processes HTML content from WARC records.

    This processor extracts readable text from HTML content by:
    1. Parsing the HTML using BeautifulSoup
    2. Removing unwanted elements (scripts, styles, etc.)
    3. Extracting text content with proper whitespace handling
    """

    def __init__(self, parser: str = 'html5lib'):
        """Initialize processor.

        Args:
            parser: HTML parser to use. Options are:
                - 'html5lib': Slower but more accurate
                - 'lxml': Faster but less accurate for malformed HTML
                - 'html.parser': Python's built-in parser
        """
        self.parser = parser
        super().__init__()

    def can_process(self, record: WarcRecord) -> bool:
        """Check if this processor can handle the record.

        Args:
            record: WARC record to check.

        Returns:
            True if record contains HTML content, False otherwise.
        """
        if not record.content_type:
            return False

        content_type = str(record.content_type).lower()
        return 'html' in content_type or 'xhtml' in content_type

    def process(self, record: WarcRecord) -> Optional[str]:
        """Process HTML content from a WARC record.

        Args:
            record: WARC record containing HTML content.

        Returns:
            Extracted text content with normalized whitespace.

        Raises:
            ValueError: If HTML parsing fails.
        """
        try:
            # Parse HTML with specified parser
            soup = BeautifulSoup(record.content, self.parser)

            # Remove unwanted elements
            for element in soup(['script', 'style', 'meta', 'link']):
                element.decompose()

            # Extract text with proper whitespace
            text = soup.get_text(separator=' ')

            # Normalize whitespace
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()

            return text

        except Exception as e:
            logger.error(
                "Failed to process HTML with parser '%s': %s",
                self.parser,
                str(e)
            )
            raise ValueError(
                f"Failed to process HTML with parser '{self.parser}': {str(e)}"
            ) from e
