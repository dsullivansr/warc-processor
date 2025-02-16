"""Tests for WarcProcessorFactory."""

import unittest
from enum import Enum, auto

from models.component_types import OutputWriters, RecordProcessors
from processing_stats import ProcessingStats
from processors.beautiful_soup_html_processor import BeautifulSoupHtmlProcessor
from processors.lexbor_html_processor import LexborHtmlProcessor
from warc_processor_factory import WarcProcessorFactory
from warc_record_parser import WarcRecordParser
from writers.json_writer import JsonWriter
from writers.plain_text_writer import PlainTextWriter


class TestWarcProcessorFactory(unittest.TestCase):
    """Test cases for WarcProcessorFactory."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = WarcProcessorFactory()

    def test_default_creation(self):
        """Test creating processor with default configuration."""
        processor = self.factory.create()
        self.assertIsInstance(processor.output_writer, PlainTextWriter)
        self.assertIsInstance(processor.record_parser, WarcRecordParser)
        self.assertIsInstance(processor.stats, ProcessingStats)
        self.assertIsInstance(processor.processors[0], LexborHtmlProcessor)

    def test_json_writer_creation(self):
        """Test creating processor with JSON writer."""
        processor = self.factory.create(output_writer=OutputWriters.JSON)
        self.assertIsInstance(processor.output_writer, JsonWriter)

    def test_lexbor_processor(self):
        """Test creating processor with LEXBOR processor."""
        processor = self.factory.create(processors=RecordProcessors.LEXBOR)
        self.assertIsInstance(processor.processors[0], LexborHtmlProcessor)

    def test_beautiful_soup_processors(self):
        """Test creating processor with BeautifulSoup processors."""
        # Test html5lib parser
        processor = self.factory.create(
            processors=RecordProcessors.BEAUTIFUL_SOUP_HTML5
        )
        self.assertIsInstance(processor.processors[0], BeautifulSoupHtmlProcessor)

        # Test lxml parser
        processor = self.factory.create(processors=RecordProcessors.BEAUTIFUL_SOUP_LXML)
        self.assertIsInstance(processor.processors[0], BeautifulSoupHtmlProcessor)

        # Test built-in parser
        processor = self.factory.create(
            processors=RecordProcessors.BEAUTIFUL_SOUP_BUILTIN
        )
        self.assertIsInstance(processor.processors[0], BeautifulSoupHtmlProcessor)

    def test_text_writer(self):
        """Test creating processor with TEXT writer."""
        processor = self.factory.create(output_writer=OutputWriters.TEXT)
        self.assertIsInstance(processor.output_writer, PlainTextWriter)

    def test_json_writer(self):
        """Test creating processor with JSON writer."""
        processor = self.factory.create(output_writer=OutputWriters.JSON)
        self.assertIsInstance(processor.output_writer, JsonWriter)

    def test_invalid_enum_values(self):
        """Test error handling for invalid enum values."""

        class InvalidProcessors(Enum):
            INVALID = auto()

        class InvalidOutputWriters(Enum):
            INVALID = auto()

        with self.assertRaises(ValueError):
            self.factory.create(processors=InvalidProcessors.INVALID)

        with self.assertRaises(ValueError):
            self.factory.create(output_writer=InvalidOutputWriters.INVALID)
