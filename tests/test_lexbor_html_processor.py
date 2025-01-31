"""Tests for LexborHtmlProcessor."""

import unittest

from processors.lexbor_html_processor import LexborHtmlProcessor
from models.warc_mime_types import ContentType
from warc_record_processor import ProcessorInput


# pylint: disable=duplicate-code
class TestLexborHtmlProcessor(unittest.TestCase):
    """Test cases for LexborHtmlProcessor class."""

    def setUp(self):
        """Set up test cases."""
        self.processor = LexborHtmlProcessor()

    def test_can_process_html(self):
        """Test can_process with HTML content."""
        content_type = ContentType('text', 'html')
        self.assertTrue(self.processor.can_process(content_type))

    def test_cannot_process_non_html(self):
        """Test can_process with non-HTML content."""
        content_type = ContentType('text', 'plain')
        self.assertFalse(self.processor.can_process(content_type))

    def test_process_html(self):
        """Test processing HTML content."""
        html = '<html><body><p>Hello world!</p></body></html>'
        processor_input = ProcessorInput(content=html,
                                         content_type=ContentType(
                                             'text', 'html'))
        result = self.processor.process(processor_input)
        self.assertEqual(result, 'Hello world!')

    def test_process_html_with_scripts(self):
        """Test processing HTML with script tags."""
        html = '''
            <html>
                <head>
                    <script>alert('test');</script>
                    <style>body { color: red; }</style>
                </head>
                <body>
                    <p>Hello world!</p>
                    <script>console.log('test');</script>
                </body>
            </html>
        '''
        processor_input = ProcessorInput(content=html,
                                         content_type=ContentType(
                                             'text', 'html'))
        result = self.processor.process(processor_input)
        self.assertEqual(result, 'Hello world!')

    def test_process_empty_content(self):
        """Test processing empty content."""
        processor_input = ProcessorInput(content='',
                                         content_type=ContentType(
                                             'text', 'html'))
        with self.assertRaises(ValueError):
            self.processor.process(processor_input)

    def test_process_whitespace_content(self):
        """Test processing whitespace content."""
        processor_input = ProcessorInput(content='   \n  ',
                                         content_type=ContentType(
                                             'text', 'html'))
        with self.assertRaises(ValueError):
            self.processor.process(processor_input)

    def test_process_invalid_html(self):
        """Test processing invalid HTML."""
        html = '<p>Hello<p>World'  # Missing closing tags
        processor_input = ProcessorInput(content=html,
                                         content_type=ContentType(
                                             'text', 'html'))
        result = self.processor.process(processor_input)
        self.assertEqual(result, 'Hello World')

    def test_process_complex_html(self):
        """Test processing complex HTML with nested elements."""
        html = '''
            <html>
                <body>
                    <div class="content">
                        <h1>Title</h1>
                        <p>Paragraph 1</p>
                        <div>
                            <p>Nested paragraph</p>
                        </div>
                    </div>
                </body>
            </html>
        '''
        processor_input = ProcessorInput(content=html,
                                         content_type=ContentType(
                                             'text', 'html'))
        result = self.processor.process(processor_input)
        self.assertEqual(result, 'Title Paragraph 1 Nested paragraph')


if __name__ == '__main__':
    unittest.main()
