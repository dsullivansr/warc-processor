"""Main entry point for WARC processor.

This module provides the main entry point for processing WARC files. The WARC processor
extracts and processes content from WARC (Web ARChive) files, which are commonly used
to store web crawl data.

Usage:
    python warc_processor_main.py [-h] [-v] input output

    Required Arguments:
        input       Path to input WARC file (can be .warc or .warc.gz)
        output      Path where the processed output should be written

    Optional Arguments:
        -h, --help  Show this help message and exit
        -v         Enable verbose logging for debugging

Examples:
    # Process a WARC file and save the output:
    python warc_processor_main.py crawl-data.warc.gz extracted-content.txt

    # Process with verbose logging:
    python warc_processor_main.py -v crawl-data.warc.gz extracted-content.txt

Input Format:
    The input should be a valid WARC file (.warc or .warc.gz) following the WARC format
    specification. Common sources for WARC files include:
    - Common Crawl (https://commoncrawl.org/the-data/get-started/)
    - Internet Archive (https://archive.org/)
    - Your own web crawls using tools like wget with --warc-file option

Output Format:
    The processor extracts text content from HTML pages in the WARC file and writes
    it to the output file. Each record is written with its metadata followed by the
    extracted content.

Requirements:
    - Python 3.6 or higher
    - Required packages (install via pip):
        pip install warcio beautifulsoup4 html5lib

Error Handling:
    - If the input WARC file doesn't exist: FileNotFoundError
    - If the output path isn't writable: PermissionError
    - Other errors will be logged with details if -v is enabled
"""

import argparse
import logging
import sys

from html_processor import HtmlProcessor
from plain_text_writer import PlainTextWriter
from warc_processor import WarcProcessor
from warc_processor_factory import WarcProcessorFactory
from output_writer import OutputWriter
from processing_stats import ProcessingStats
from warc_record_parser import WarcRecordParser
from warc_record_processor_chain import WarcRecordProcessorChain

logger = logging.getLogger(__name__)

def main(args=None):
    """Main entry point.
    
    Args:
        args: Optional command line arguments.
        
    Returns:
        0 on success, non-zero on error.
    """
    if args is None:
        args = sys.argv[1:]
        
    parser = argparse.ArgumentParser(description='Process WARC files.')
    parser.add_argument('input', help='Input WARC file')
    parser.add_argument('output', help='Output file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    
    try:
        parsed_args = parser.parse_args(args)
        
        # Setup logging
        log_level = logging.DEBUG if parsed_args.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create processor components
        processors = [HtmlProcessor()]
        processor_chain = WarcRecordProcessorChain(processors)
        record_parser = WarcRecordParser()
        stats = ProcessingStats()
        output_writer = PlainTextWriter()
        
        # Create processor
        processor = WarcProcessor(
            processors=processors,
            output_writer=output_writer,
            record_parser=record_parser,
            stats=stats,
            processor_chain=processor_chain
        )
        
        # Process file
        stats = processor.process_warc_file(parsed_args.input, parsed_args.output)
        
        # Print summary
        print("\nProcessing complete:")
        print(f"- Input size: {stats.input_size / (1024*1024):.1f} MB")
        print(f"- Records processed: {stats.records_processed}")
        print(f"- Records skipped: {stats.records_skipped}")
        print(f"- Records failed: {stats.records_failed}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
        
        
if __name__ == '__main__':
    sys.exit(main())
