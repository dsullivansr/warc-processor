"""Test script for WARC processing."""

import sys
import os
import logging

from html_processor import HtmlProcessor
from warc_processor import WarcProcessor

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python test_processor.py <warc_file>")
        sys.exit(1)
        
    warc_path = sys.argv[1]
    if not os.path.exists(warc_path):
        print(f"Error: File not found: {warc_path}")
        sys.exit(1)
        
    logger.info(f"Processing WARC file: {warc_path}")
    logger.info(f"File size: {os.path.getsize(warc_path) / (1024*1024):.2f} MB")
    
    # Create output path in same directory as input
    output_path = os.path.join(
        os.path.dirname(warc_path),
        os.path.basename(warc_path) + '.processed.txt'
    )
    
    # Create processor with HTML handler
    processor = WarcProcessor([HtmlProcessor()])
    
    try:
        # Process the file
        logger.info("Starting processing...")
        stats = processor.process_warc_file(warc_path, output_path)
        
        # Print results
        logger.info("\nProcessing complete!")
        logger.info(f"Output written to: {output_path}")
        logger.info("\nStatistics:")
        for key, value in stats.items():
            logger.info(f"{key}: {value}")
            
    except Exception as e:
        logger.error(f"Error processing file: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
