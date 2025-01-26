"""WARC identifiers.

This module contains classes for WARC identifiers like URIs and record IDs.
"""

from urllib.parse import urlparse


class WarcUri:
    """Represents a WARC target URI."""

    def __init__(self, uri: str):
        """Creates a WARC URI.
        
        Args:
            uri: The URI string.
            
        Raises:
            ValueError: If URI is invalid.
        """
        if not uri:
            raise ValueError("URI cannot be empty")

        try:
            parsed = urlparse(uri)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Invalid URI format")
        except Exception as e:
            raise ValueError(f"Invalid URI: {e}") from e

        self.uri = uri

    def __str__(self) -> str:
        """Returns string representation."""
        return self.uri

    def __eq__(self, other) -> bool:
        """Checks equality with another URI."""
        if isinstance(other, WarcUri):
            return self.uri == other.uri
        return self.uri == str(other)

    @classmethod
    def from_str(cls, uri: str) -> 'WarcUri':
        """Creates a WarcUri from a string.
        
        Args:
            uri: The URI string.
            
        Returns:
            WarcUri instance.
        """
        return cls(uri)


class WarcRecordId:
    """Represents a WARC record ID."""

    def __init__(self, record_id: str):
        """Creates a WARC record ID.
        
        Args:
            record_id: The record ID string.
        """
        self.record_id = record_id

    def __str__(self) -> str:
        """Returns string representation."""
        return self.record_id

    def __eq__(self, other) -> bool:
        """Checks equality with another record ID."""
        if isinstance(other, WarcRecordId):
            return self.record_id == other.record_id
        return self.record_id == str(other)


class PayloadDigest:
    """Represents a WARC payload digest."""

    def __init__(self, digest: str):
        """Creates a WARC payload digest.
        
        Args:
            digest: The digest string.
        """
        self.digest = digest

    def __str__(self) -> str:
        """Returns string representation."""
        return self.digest

    def __eq__(self, other) -> bool:
        """Checks equality with another digest."""
        if isinstance(other, PayloadDigest):
            return self.digest == other.digest
        return self.digest == str(other)
