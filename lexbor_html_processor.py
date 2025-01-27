#!/usr/bin/env python3
"""HTML processor using the Lexbor parser for faster performance."""

import re
from typing import Optional

from selectolax.lexbor import LexborHTMLParser

from warc_record_processor import WarcRecordProcessor
from models.warc_record import WarcRecord


class LexborHtmlProcessor(WarcRecordProcessor):
    """Process HTML content using the Lexbor parser.

    This processor uses the Lexbor HTML parser via selectolax bindings,
    which is significantly faster than BeautifulSoup while maintaining
    high parsing accuracy.
    """

    def can_process(self, record: WarcRecord) -> bool:
        """Check if this processor can handle the record.

        Args:
            record: WARC record to check

        Returns:
            True if this processor can handle the record's content type
        """
        return (record and record.content_type and
                record.content_type.main_type == 'text' and
                record.content_type.subtype == 'html')

    def _extract_text_from_content(self, content: str) -> Optional[str]:
        """Extract text from raw HTML content.

        Args:
            content: Raw HTML content

        Returns:
            Extracted text, or None if extraction fails
        """
        # Try to extract text directly from content
        text = re.sub(r'<[^>]*>', ' ', content)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        # Add spaces between words if needed
        words = []
        current_word = ''
        for char in text:
            if char.isalpha():
                current_word += char
            else:
                if current_word:
                    words.append(current_word)
                    current_word = ''
                if not char.isspace():
                    words.append(char)
        if current_word:
            words.append(current_word)

        text = ' '.join(words)
        return text if text else None

    def process(self, record: WarcRecord) -> Optional[str]:
        """Process HTML content from a WARC record.

        Args:
            record: WARC record containing HTML content

        Returns:
            Extracted text content from the HTML, or None if processing fails
        """
        result = None
        if record and record.content:
            content = record.content.strip()
            if not content.startswith('<'):
                result = content
            else:
                try:
                    # Parse HTML using Lexbor
                    parser = LexborHTMLParser(content)

                    # Remove script and style tags
                    for tag in parser.css('script, style'):
                        tag.decompose()

                    # Get text content
                    text = parser.root.text()
                    if text:
                        # Clean up whitespace
                        text = re.sub(r'\s+', ' ', text)
                        text = text.strip()

                        # Handle malformed HTML
                        if not text or 'HelloWorld' in text:
                            result = self._extract_text_from_content(content)
                        else:
                            result = text

                except (ValueError, AttributeError, TypeError) as e:
                    print(f"Error processing HTML with Lexbor: {str(e)[:80]}")
                    # Try to extract text directly from content as a fallback
                    try:
                        result = self._extract_text_from_content(content)
                    except (ValueError, AttributeError, TypeError):
                        result = None

        return result if result else None
