#!/usr/bin/env python3
"""Lexbor HTML processor implementation."""

import logging

from selectolax.lexbor import LexborHTMLParser

from models.warc_record import WarcRecord
from warc_record_processor import ProcessorInput, WarcRecordProcessor

logger = logging.getLogger(__name__)


class LexborHtmlProcessor(WarcRecordProcessor):
    """HTML processor that uses the Lexbor engine for parsing."""

    def can_process(self, processor_input) -> bool:
        """Check if this processor can handle the input.

        This processor only handles standard HTML content (text/html).
        For XHTML content, use BeautifulSoupHtmlProcessor.

        Args:
            processor_input: Input to potentially process (ProcessorInput or ContentType)

        Returns:
            True if content is HTML and processable, False otherwise
        """
        # Handle both ProcessorInput and ContentType for backward compatibility
        if hasattr(processor_input, "content_type"):
            content_type = processor_input.content_type
            content = processor_input.content
        else:
            content_type = processor_input
            content = None

        if not content_type:
            return False

        # First check content type - only handle text/html
        if not (content_type.main_type == "text" and content_type.subtype == "html"):
            return False

        # Then check if content is processable (only for ProcessorInput)
        if content is not None:
            return bool(content and not content.isspace())

        return True

    def process(self, processor_input: WarcRecord) -> str:
        """Process HTML content using Lexbor.

        Args:
            processor_input: WARC record to process

        Returns:
            Extracted text content

        Raises:
            ValueError: If content is empty or whitespace
        """
        if not processor_input.content or (
            processor_input.content.isspace()
        ):
            raise ValueError("Content is empty or whitespace")

        try:
            # Parse HTML using Lexbor
            parser = LexborHTMLParser(processor_input.content)

            # Remove script and style elements
            for node in parser.css("script, style"):
                node.decompose()

            # Extract text content from each text node
            text_nodes = []
            for node in parser.root.traverse():
                if node.text(deep=False, strip=True):
                    text_nodes.append(node.text(deep=False, strip=True))
            return " ".join(text_nodes)
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to parse HTML: %s", str(e))
            raise ValueError(f"Failed to parse HTML: {str(e)}") from e
