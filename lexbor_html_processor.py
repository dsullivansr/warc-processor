#!/usr/bin/env python3
"""Lexbor HTML processor implementation."""

import logging

import lxml.html  # pylint: disable=no-member

from models.warc_mime_types import ContentType
from warc_record_processor import ProcessorInput, WarcRecordProcessor

logger = logging.getLogger(__name__)


class LexborHtmlProcessor(WarcRecordProcessor):
    """HTML processor that uses Lexbor for parsing."""

    def can_process(self, content_type: ContentType) -> bool:
        """Check if this processor can handle the content type.

        This processor only handles standard HTML content (text/html).
        For XHTML content, use BeautifulSoupHtmlProcessor.

        Args:
            content_type: Content type to check

        Returns:
            True if this processor can handle the content type
        """
        if not content_type:
            return False

        # Only handle text/html, not application/xhtml+xml
        return (content_type.main_type == 'text' and
                content_type.subtype == 'html')

    def process(self, processor_input: ProcessorInput) -> str:
        """Process HTML content using Lexbor.

        Args:
            processor_input: Input to process

        Returns:
            Extracted text content

        Raises:
            ValueError: If content is empty or whitespace
        """
        if not processor_input.content or processor_input.content.isspace():
            raise ValueError("Content is empty or whitespace")

        try:
            # Parse HTML
            doc = lxml.html.fromstring(processor_input.content)

            # Remove script and style elements
            for element in doc.xpath('//script | //style'):
                element.getparent().remove(element)

            # Extract text content
            text = ' '.join(doc.xpath('//text()'))
            return ' '.join(text.split())
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to parse HTML: %s", str(e))
            raise ValueError(f"Failed to parse HTML: {str(e)}") from e
