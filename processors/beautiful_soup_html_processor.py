"""BeautifulSoup HTML processor implementation."""

import logging

import bs4

from models.warc_mime_types import ContentType
from warc_record_processor import ProcessorInput, WarcRecordProcessor

logger = logging.getLogger(__name__)


class BeautifulSoupHtmlProcessor(WarcRecordProcessor):
    """Processes HTML content using BeautifulSoup.

    This processor extracts readable text from HTML content by:
    1. Parsing the HTML using BeautifulSoup
    2. Removing unwanted elements (scripts, styles, etc.)
    3. Extracting text content with proper whitespace handling
    """

    def __init__(self, parser: str = "html5lib"):
        """Initialize processor.

        Args:
            parser: HTML parser to use. Options are:
                - 'html5lib': Slower but more accurate
                - 'lxml': Faster but less accurate for malformed HTML
                - 'html.parser': Python's built-in parser
        """
        self.parser = parser
        super().__init__()

    def can_process(self, content_type: ContentType) -> bool:
        """Check if this processor can handle the content type.

        This processor handles both HTML (text/html) and XHTML.
        For standard HTML content, consider using LexborHtmlProcessor.

        Args:
            content_type: Type of content to check.

        Returns:
            True if content is HTML or XHTML, False otherwise.
        """
        if not content_type:
            return False

        # Handle both text/html and application/xhtml+xml
        if content_type.main_type == "text" and content_type.subtype == "html":
            return True
        if (
            content_type.main_type == "application"
            and content_type.subtype == "xhtml+xml"
        ):
            return True

        return False

    def process(self, processor_input: ProcessorInput) -> str:
        """Process HTML content using BeautifulSoup.

        Args:
            processor_input: Input to process

        Returns:
            Extracted text content

        Raises:
            ValueError: If content is empty or whitespace
        """
        if not processor_input.content or processor_input.content.isspace():
            raise ValueError("Content cannot be empty or whitespace")

        try:
            soup = bs4.BeautifulSoup(processor_input.content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Extract text with preserved whitespace
            text = " ".join(line.strip() for line in soup.stripped_strings)

            return text
        except Exception as e:
            raise ValueError(f"HTML processing failed: {str(e)}") from e
