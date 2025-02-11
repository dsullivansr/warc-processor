"""Type definitions for WARC processor components."""

from enum import Enum, auto


class OutputWriters(Enum):
    """Available output writer types."""
    DEFAULT = auto()  # PlainTextWriter
    TEXT = auto()     # PlainTextWriter
    JSON = auto()


class RecordProcessors(Enum):
    """Available record processor types.

    BeautifulSoup parsers:
    - BEAUTIFUL_SOUP_LXML: Very fast, lenient HTML parsing (recommended)
    - BEAUTIFUL_SOUP_HTML5: Most lenient, browser-like parsing but slow
    - BEAUTIFUL_SOUP_BUILTIN: Python's built-in parser, decent speed
    """
    DEFAULT = auto()                # LexborHtmlProcessor
    LEXBOR = auto()                # LexborHtmlProcessor
    BEAUTIFUL_SOUP_LXML = auto()    # BeautifulSoupHtmlProcessor with lxml
    BEAUTIFUL_SOUP_HTML5 = auto()   # BeautifulSoupHtmlProcessor with html5lib
    BEAUTIFUL_SOUP_BUILTIN = auto()  # BeautifulSoup with html.parser


class RecordParsers(Enum):
    """Available record parser types."""
    DEFAULT = auto()


class ProcessingStats(Enum):
    """Available processing stats types."""
    DEFAULT = auto()
