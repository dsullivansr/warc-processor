"""Tests for WARC path handling.

This module contains unit tests for WARC file path validation and handling.
"""

import os
import tempfile
import unittest
from pathlib import Path

from models.warc_paths import OutputPath, WarcPath


class TestWarcPath(unittest.TestCase):
    """Test cases for WarcPath class."""
    
    def test_valid_warc_path(self):
        """Tests valid WARC file paths."""
        # Test .warc extension
        path = WarcPath.from_str('test.warc')
        self.assertEqual(path.path, Path('test.warc'))
        
        # Test .warc.gz extension
        path = WarcPath.from_str('test.warc.gz')
        self.assertEqual(path.path, Path('test.warc.gz'))
        
    def test_invalid_warc_path(self):
        """Tests rejection of invalid WARC file paths."""
        invalid_paths = [
            'test.txt',  # Wrong extension
            'test.war',  # Similar but wrong extension
            'test.gz',  # Just gz extension
            'test.warc.txt',  # Wrong secondary extension
            '.warc',  # No filename
            '',  # Empty string
        ]
        
        for invalid_path in invalid_paths:
            with self.assertRaises(ValueError):
                WarcPath.from_str(invalid_path)
                
    def test_string_representation(self):
        """Tests string conversion."""
        path_str = 'test.warc'
        path = WarcPath.from_str(path_str)
        self.assertEqual(str(path), path_str)


class TestOutputPath(unittest.TestCase):
    """Test cases for OutputPath class."""
    
    def setUp(self):
        """Creates a temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        # Create a read-only directory
        self.readonly_dir = os.path.join(self.temp_dir, 'readonly')
        os.mkdir(self.readonly_dir)
        os.chmod(self.readonly_dir, 0o555)  # Read and execute only
        
    def tearDown(self):
        """Cleans up temporary files."""
        os.chmod(self.readonly_dir, 0o755)  # Restore write permissions
        os.rmdir(self.readonly_dir)
        os.rmdir(self.temp_dir)
        
    def test_valid_output_path(self):
        """Tests valid output paths."""
        # Test path in existing directory
        path = os.path.join(self.temp_dir, 'output.txt')
        out_path = OutputPath.from_str(path)
        self.assertEqual(out_path.path, Path(path))
        
    def test_nonexistent_directory(self):
        """Tests rejection of paths in nonexistent directories."""
        path = os.path.join(self.temp_dir, 'nonexistent', 'output.txt')
        with self.assertRaises(ValueError):
            OutputPath.from_str(path)
            
    def test_readonly_directory(self):
        """Tests rejection of paths in read-only directories."""
        path = os.path.join(self.readonly_dir, 'output.txt')
        with self.assertRaises(ValueError):
            OutputPath.from_str(path)
            
    def test_string_representation(self):
        """Tests string conversion."""
        path_str = os.path.join(self.temp_dir, 'output.txt')
        path = OutputPath.from_str(path_str)
        self.assertEqual(str(path), path_str)


if __name__ == '__main__':
    unittest.main()
