"""Tests for WARC identifiers.

This module contains tests for WARC identifiers like URIs and record IDs.
"""

import unittest

from models.warc_identifiers import PayloadDigest, WarcRecordId, WarcUri


class TestWarcUri(unittest.TestCase):
    """Test cases for WARC URIs."""

    def test_valid_uri(self):
        """Tests creating a valid URI."""
        uri = WarcUri('http://example.com')
        self.assertEqual(str(uri), 'http://example.com')
        self.assertEqual(uri, 'http://example.com')

    def test_invalid_uri(self):
        """Tests creating an invalid URI."""
        with self.assertRaises(ValueError):
            WarcUri('not-a-uri')

        with self.assertRaises(ValueError):
            WarcUri('')

    def test_string_representation(self):
        """Tests string representation."""
        uri = WarcUri('http://example.com')
        self.assertEqual(str(uri), 'http://example.com')

    def test_equality(self):
        """Tests equality comparison."""
        uri1 = WarcUri('http://example.com')
        uri2 = WarcUri('http://example.com')
        uri3 = WarcUri('http://other.com')

        self.assertEqual(uri1, uri2)
        self.assertNotEqual(uri1, uri3)
        self.assertEqual(uri1, 'http://example.com')
        self.assertNotEqual(uri1, 'http://other.com')


class TestWarcIdentifiers(unittest.TestCase):
    """Test cases for WARC identifiers."""

    def test_warc_record_id(self):
        """Tests WARC record ID."""
        record_id = WarcRecordId('<urn:uuid:12345678>')
        self.assertEqual(str(record_id), '<urn:uuid:12345678>')
        self.assertEqual(record_id, '<urn:uuid:12345678>')

        # Test equality
        other_id = WarcRecordId('<urn:uuid:12345678>')
        self.assertEqual(record_id, other_id)
        self.assertEqual(record_id, '<urn:uuid:12345678>')
        self.assertNotEqual(record_id, '<urn:uuid:87654321>')

    def test_payload_digest(self):
        """Tests payload digest."""
        digest = PayloadDigest('sha1:2fd4e1c67a2d28fced849ee1bb76e7391b93eb12')
        self.assertEqual(str(digest),
                         'sha1:2fd4e1c67a2d28fced849ee1bb76e7391b93eb12')
        self.assertEqual(digest,
                         'sha1:2fd4e1c67a2d28fced849ee1bb76e7391b93eb12')

        # Test equality
        other_digest = PayloadDigest(
            'sha1:2fd4e1c67a2d28fced849ee1bb76e7391b93eb12')
        self.assertEqual(digest, other_digest)
        self.assertEqual(digest,
                         'sha1:2fd4e1c67a2d28fced849ee1bb76e7391b93eb12')
        self.assertNotEqual(digest, 'sha1:different')


if __name__ == '__main__':
    unittest.main()
