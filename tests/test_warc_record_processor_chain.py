"""Tests for the WarcRecordProcessorChain class."""

from unittest import TestCase
from unittest.mock import MagicMock

from warc_record_processor import WarcRecordProcessor
from warc_record_processor_chain import WarcRecordProcessorChain
from models.warc_record import WarcRecord


class TestWarcRecordProcessorChain(TestCase):
    """Tests for the WarcRecordProcessorChain class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock processor
        self.mock_processor = MagicMock(spec=WarcRecordProcessor)
        
        # Create chain
        self.chain = WarcRecordProcessorChain([self.mock_processor])
        
        # Create test record
        self.record = WarcRecord(
            record_id='test-id',
            record_type='response',
            target_uri='http://example.com',
            date='2025-01-24T12:34:56Z',
            content_type='text/html',
            content_length=100,
            content='test content',
            headers={}
        )
        
    def test_process_html_record(self):
        """Test processing HTML record."""
        # Configure mock
        self.mock_processor.can_process.return_value = True
        self.mock_processor.process.return_value = 'processed content'
        
        # Process record
        result = self.chain.process(self.record)
        
        # Verify result
        self.assertEqual(result, 'processed content')
        self.mock_processor.can_process.assert_called_once_with(self.record)
        self.mock_processor.process.assert_called_once_with(self.record)
        
    def test_process_non_html_record(self):
        """Test processing non-HTML record."""
        # Configure record
        self.record.content_type = 'text/plain'
        
        # Configure mock
        self.mock_processor.can_process.return_value = False
        
        # Process record
        result = self.chain.process(self.record)
        
        # Verify result
        self.assertIsNone(result)
        
    def test_process_no_matching_processor(self):
        """Test when no processor matches."""
        # Configure mock
        self.mock_processor.can_process.return_value = False
        
        # Process record
        result = self.chain.process(self.record)
        
        # Verify result
        self.assertIsNone(result)
        self.mock_processor.can_process.assert_called_once_with(self.record)
        self.mock_processor.process.assert_not_called()
        
    def test_process_processor_error(self):
        """Test handling processor error."""
        # Configure mock
        self.mock_processor.can_process.return_value = True
        self.mock_processor.process.side_effect = Exception('test error')
        
        # Process record
        result = self.chain.process(self.record)
        
        # Verify result
        self.assertIsNone(result)
        self.mock_processor.can_process.assert_called_once_with(self.record)
        self.mock_processor.process.assert_called_once_with(self.record)
        
    def test_multiple_processors(self):
        """Test with multiple processors."""
        # Create second mock processor
        mock_processor2 = MagicMock(spec=WarcRecordProcessor)
        chain = WarcRecordProcessorChain([self.mock_processor, mock_processor2])
        
        # Configure first mock to fail
        self.mock_processor.can_process.return_value = True
        self.mock_processor.process.return_value = None
        
        # Configure second mock to succeed
        mock_processor2.can_process.return_value = True
        mock_processor2.process.return_value = 'processed by second'
        
        # Process record
        result = chain.process(self.record)
        
        # Verify result
        self.assertEqual(result, 'processed by second')
        self.mock_processor.can_process.assert_called_once_with(self.record)
        self.mock_processor.process.assert_called_once_with(self.record)
        mock_processor2.can_process.assert_called_once_with(self.record)
        mock_processor2.process.assert_called_once_with(self.record)


if __name__ == '__main__':
    unittest.main()
