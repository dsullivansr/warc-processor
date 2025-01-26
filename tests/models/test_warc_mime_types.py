"""Tests for MIME type handling.

This module contains unit tests for MIME type validation and matching.
"""

import unittest

from models.warc_mime_types import ContentType, ContentTypeError


class TestContentType(unittest.TestCase):
    """Test cases for ContentType class."""

    def test_valid_content_type(self):
        """Tests parsing of valid content types."""
        ct = ContentType('text/html')
        self.assertEqual(ct.main_type, 'text')
        self.assertEqual(ct.subtype, 'html')
        self.assertEqual(ct.parameters, {})

    def test_content_type_with_parameters(self):
        """Tests parsing of content types with parameters."""
        ct = ContentType('text/html; charset=utf-8; boundary=something')
        self.assertEqual(ct.main_type, 'text')
        self.assertEqual(ct.subtype, 'html')
        self.assertEqual(ct.parameters, {
            'charset': 'utf-8',
            'boundary': 'something'
        })

    def test_case_insensitive(self):
        """Tests case-insensitive handling."""
        ct = ContentType('Text/HTML; Charset=UTF-8')
        self.assertEqual(ct.main_type, 'text')
        self.assertEqual(ct.subtype, 'html')
        self.assertEqual(ct.parameters['charset'], 'UTF-8')

    def test_invalid_content_type(self):
        """Tests rejection of invalid content types."""
        invalid_types = [
            '',  # Empty
            'text',  # Missing subtype
            'text/',  # Empty subtype
            '/html',  # Empty main type
            'text/html; invalid',  # Invalid parameter format
            'text/html; =value',  # Missing parameter name
            'text/html; param=',  # Missing parameter value
            'text//html',  # Double slash
            'text/html/',  # Trailing slash
        ]

        for invalid_type in invalid_types:
            with self.assertRaises(ContentTypeError):
                ContentType(invalid_type)

    def test_string_representation(self):
        """Tests string conversion."""
        type_str = 'text/html; charset=utf-8'
        ct = ContentType(type_str)
        self.assertEqual(str(ct), type_str)

    def test_equality(self):
        """Tests equality comparison."""
        ct1 = ContentType('text/html; charset=utf-8')
        ct2 = ContentType('text/html; charset=ascii')  # Different param
        ct3 = ContentType('text/plain')  # Different subtype
        ct4 = ContentType('application/html')  # Different main type

        self.assertEqual(ct1, ct2)  # Parameters don't affect equality
        self.assertNotEqual(ct1, ct3)
        self.assertNotEqual(ct1, ct4)
        self.assertNotEqual(ct3, ct4)
        self.assertNotEqual(ct1, 'text/html')  # Different type

    def test_pattern_matching(self):
        """Tests pattern matching functionality."""
        ct = ContentType('text/html; charset=utf-8')

        # Valid patterns
        self.assertTrue(ct.matches('text/html'))
        self.assertTrue(ct.matches('text/*'))
        self.assertTrue(ct.matches('*/html'))
        self.assertTrue(ct.matches('*/*'))

        # Non-matching patterns
        self.assertFalse(ct.matches('text/plain'))
        self.assertFalse(ct.matches('application/*'))
        self.assertFalse(ct.matches('*/plain'))

        # Invalid patterns
        self.assertFalse(ct.matches('text'))
        self.assertFalse(ct.matches('*/'))
        self.assertFalse(ct.matches('/html'))
        self.assertFalse(ct.matches(''))


if __name__ == '__main__':
    unittest.main()
