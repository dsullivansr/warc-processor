"""MIME type handling for WARC records."""

import re
from typing import Dict, Optional

# Regular expression for validating MIME types
MIME_TYPE_PATTERN = re.compile(
    r'^[a-zA-Z0-9]+/[a-zA-Z0-9+\-_.]+(?:\s*;\s*[a-zA-Z0-9]+=[a-zA-Z0-9\-]+)*$')


class ContentTypeError(ValueError):
    """Error raised when content type is invalid."""


class ContentType:
    """Content type representation."""

    def __init__(self,
                 type_str_or_main_type: str,
                 subtype: Optional[str] = None,
                 parameters: Optional[Dict[str, str]] = None):
        """Initialize ContentType.

        Can be initialized in two ways:
        1. With a MIME type string: ContentType('text/html;charset=utf-8')
        2. With separate parts: ContentType('text', 'html', {'charset':'utf-8'})

        Args:
            type_str_or_main_type: Type string or main type
            subtype: Subtype if using separate parts
            parameters: Optional parameters if using separate parts

        Raises:
            ContentTypeError: If the content type is invalid
        """
        if not type_str_or_main_type:
            raise ContentTypeError("Content type string cannot be empty")

        if subtype is None:
            # Parse type string
            parts = type_str_or_main_type.split(';')
            type_parts = parts[0].strip().split('/')
            if len(type_parts) != 2:
                raise ContentTypeError("Invalid content type string")

            main_type = type_parts[0].strip()
            subtype = type_parts[1].strip()

            if not main_type or not subtype:
                raise ContentTypeError("Main type and subtype cannot be empty")

            if '//' in type_str_or_main_type:
                raise ContentTypeError("Invalid content type string")

            self.main_type = main_type.lower()
            self.subtype = subtype.lower()

            # Parse parameters
            self.parameters = {}
            for part in parts[1:]:
                param_parts = part.strip().split('=', 1)
                if len(param_parts) != 2:
                    raise ContentTypeError("Invalid parameter format")
                key = param_parts[0].strip()
                value = param_parts[1].strip()
                if not key or not value:
                    msg = "Parameter name and value cannot be empty"
                    raise ContentTypeError(msg)
                self.parameters[key.lower()] = value
        else:
            # Use provided parts
            if not subtype:
                raise ContentTypeError("Subtype cannot be empty")

            self.main_type = type_str_or_main_type.lower()
            self.subtype = subtype.lower()
            self.parameters = parameters or {}

    def __str__(self) -> str:
        """Return string representation of content type.

        Returns:
            String representation of content type
        """
        type_str = f"{self.main_type}/{self.subtype}"
        if self.parameters:
            params = [f"{k}={v}" for k, v in self.parameters.items()]
            type_str += "; " + "; ".join(params)
        return type_str

    def __eq__(self, other: object) -> bool:
        """Check equality with another ContentType."""
        if not isinstance(other, ContentType):
            return NotImplemented
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
