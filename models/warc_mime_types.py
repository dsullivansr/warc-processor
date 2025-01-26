"""MIME type handling for WARC records.

This module provides functionality for parsing and validating MIME types.
"""

import re

# Regular expression for validating MIME types
MIME_TYPE_PATTERN = re.compile(
    r'^[a-zA-Z0-9]+/[a-zA-Z0-9+\-_.]+(?:\s*;\s*[a-zA-Z0-9]+=[a-zA-Z0-9\-]+)*$')


class ContentTypeError(ValueError):
    """Error raised when content type is invalid."""


class ContentType:
    """Represents a MIME content type.

    Attributes:
        raw_type: Original content type string
        main_type: Main type (e.g. 'text' in 'text/html')
        subtype: Subtype (e.g. 'html' in 'text/html')
        parameters: Dictionary of parameters
    """

    def __init__(self, content_type: str):
        """Initialize content type.

        Args:
            content_type: MIME type string (e.g. 'text/html; charset=utf-8')

        Raises:
            ContentTypeError: If the content type is invalid.
        """
        if not MIME_TYPE_PATTERN.match(content_type):
            raise ContentTypeError(
                f"Invalid content type format: {content_type}")

        self.raw_type = content_type
        parts = content_type.split(';', 1)
        type_parts = parts[0].strip().split('/')

        self.main_type = type_parts[0].lower()
        self.subtype = type_parts[1].lower()
        self.parameters = {}

        if len(parts) > 1:
            for param in parts[1].split(';'):
                if '=' in param:
                    key, value = param.strip().split('=', 1)
                    self.parameters[key.lower()] = value

    def __str__(self) -> str:
        """Get string representation with parameters."""
        base = f"{self.main_type}/{self.subtype}"
        if not self.parameters:
            return base
        params = '; '.join(
            f"{k}={v}" for k, v in sorted(self.parameters.items()))
        return f"{base}; {params}"

    def __eq__(self, other) -> bool:
        """Check equality with another content type.
        
        Args:
            other: Object to compare with

        Returns:
            True if main_type and subtype match, ignoring parameters
        """
        if not isinstance(other, ContentType):
            return False
        return (self.main_type == other.main_type and
                self.subtype == other.subtype)

    def matches(self, pattern: str) -> bool:
        """Check if content type matches a pattern.

        Args:
            pattern: Pattern to match (e.g. 'text/*', '*/html')

        Returns:
            True if matches, False otherwise
        """
        if pattern == '*/*':
            return True

        if '/' not in pattern:
            return False

        pattern_main, pattern_sub = pattern.split('/')
        return (pattern_main in {'*', self.main_type} and
                pattern_sub in {'*', self.subtype})
