from typing import List

from langdetect import LangDetectException, detect

from models.warc_record import ProcessedWarcRecord
from warc_record_processor import ProcessorInput, WarcRecordProcessor


class LanguageDetector(WarcRecordProcessor):
    """Detects the language of processed text content.

    This processor first checks the Content-Language header from the original
    HTTP response. If not present, it detects the language using langdetect
    and adds it as a Content-Language header.
    """

    def can_process(self, processor_input: ProcessorInput) -> bool:
        """Check if content can be processed.

        We can process any text-based content.

        Args:
            processor_input: Input to check

        Returns:
            True if content is text-based and can be processed
        """
        return processor_input.content_type.is_text

    def _normalize_language_code(self, code: str) -> str:
        """Normalize a language code to a standard format.

        Examples:
            en-US -> en
            en-GB -> en
            de-DE -> de
            sv-SE -> sv

        Args:
            code: Language code to normalize

        Returns:
            Normalized language code (usually 2-letter code)
        """
        # Remove any whitespace
        code = code.strip()

        # Take first part of compound codes (e.g., 'en-US' -> 'en')
        if "-" in code:
            code = code.split("-")[0]

        return code.lower()

    def _parse_content_language(self, header: str) -> List[str]:
        """Parse Content-Language header value.

        Examples:
            'en-US' -> ['en']
            'sv-SE, sv, en' -> ['sv', 'sv', 'en']
            'en-GB' -> ['en']

        Args:
            header: Content-Language header value

        Returns:
            List of normalized language codes
        """
        if not header:
            return []

        # Split on comma and normalize each code
        langs = [self._normalize_language_code(lang) for lang in header.split(",")]

        # Remove duplicates while preserving order
        seen = set()
        return [lang for lang in langs if not (lang in seen or seen.add(lang))]

    def process(self, record: ProcessedWarcRecord) -> None:
        """Detect the language of the processed content.

        Args:
            record: Record to process and update with language info

        Raises:
            ValueError: If content is empty or language detection fails
        """
        # Skip if no processable content
        if not record.processed_content or record.processed_content.isspace():
            return

        # Initialize metadata if needed
        if record.metadata is None:
            record.metadata = {}

        # First check if Content-Language header exists
        if record.record and record.record.headers:
            content_lang = record.record.headers.get("Content-Language")
            if content_lang:
                # Parse and normalize language codes
                langs = self._parse_content_language(content_lang)
                if langs:
                    # Store primary and all languages
                    record.metadata["language"] = langs[0]
                    if len(langs) > 1:
                        record.metadata["all_languages"] = langs
                    record.metadata["language_source"] = "http_header"
                    return

        try:
            # Detect the language
            lang = detect(record.processed_content)
            lang = self._normalize_language_code(lang)

            # Add to HTTP headers
            if record.record:
                if record.record.headers is None:
                    record.record.headers = {}
                record.record.headers["Content-Language"] = lang

            # Add to metadata
            record.metadata["language"] = lang
            record.metadata["language_source"] = "detected"

        except LangDetectException as e:
            raise ValueError(f"Language detection failed: {str(e)}") from e
