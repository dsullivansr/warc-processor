"""MIME type handling and validation.

This module provides functionality for handling and validating MIME content types
used in WARC records.
"""

import re


# Regular expression for validating MIME types
MIME_TYPE_PATTERN = re.compile(
    r'^[a-zA-Z0-9]+/[a-zA-Z0-9+\-_.]+(?:\s*;\s*[a-zA-Z0-9]+=[a-zA-Z0-9\-]+)*$'
)


class ContentTypeError(ValueError):
    """Raised when a content type is invalid."""
    pass


class ContentType:
    """Represents a validated MIME content type.
    
    This class ensures that content types follow the standard format:
    type/subtype[;parameter=value]*.
    
    Attributes:
        raw_type: The original content type string.
        main_type: The main type (e.g., 'text' in 'text/html').
        subtype: The subtype (e.g., 'html' in 'text/html').
        parameters: Optional dictionary of parameters.
    """
    
    def __init__(self, content_type: str):
        """Creates a new ContentType instance.
        
        Args:
            content_type: The content type string to validate.
            
        Raises:
            ContentTypeError: If the content type is invalid.
        """
        if not MIME_TYPE_PATTERN.match(content_type):
            raise ContentTypeError(f"Invalid content type format: {content_type}")
        
        self.raw_type = content_type
        parts = content_type.split(';', 1)
        type_parts = parts[0].strip().split('/', 1)
        
        self.main_type = type_parts[0].lower()
        
        if len(type_parts) > 1:
            self.subtype = type_parts[1].lower()
        else:
            self.subtype = ''
            
        self.parameters = {}
        
        if len(parts) > 1:
            for param in parts[1].split(';'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    self.parameters[key.strip().lower()] = value.strip()
    
    def __str__(self) -> str:
        return self.raw_type
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ContentType):
            return False
            
        return (self.main_type == other.main_type and 
                self.subtype == other.subtype)
    
    def matches(self, pattern: str) -> bool:
        """Checks if this content type matches a pattern.
        
        The pattern can use wildcards, e.g., 'text/*' matches any text type.
        
        Args:
            pattern: The pattern to match against.
            
        Returns:
            True if the content type matches the pattern.
        """
        if '/' not in pattern:
            return False
        
        pattern_main, pattern_sub = pattern.lower().split('/', 1)
        
        if pattern_main == '*' or pattern_main == self.main_type:
            if pattern_sub == '*' or pattern_sub == self.subtype:
                return True
        return False
