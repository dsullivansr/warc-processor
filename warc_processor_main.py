"""Main entry point for WARC processing.

This module provides the main entry point and command line interface for
processing WARC files.
"""

import argparse
import logging
import sys
from typing import List, Optional

from html_processor import HtmlProcessor
from plain_text_writer import PlainTextWriter
from processing_stats import ProcessingStats
from warc_processor import WarcProcessor
from warc_processor_factory import WarcProcessorFactory
from warc_record_parser import WarcRecordParser
from warc_record_processor_chain import WarcRecordProcessorChain


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments.
    
    Args:
        args: List of command line arguments. If None, sys.argv[1:] is used.
        
    Returns:
        Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="""Process WARC files to extract content.
        
        This tool processes WARC (Web ARChive) files according to the ISO 28500
        specification. Common sources for WARC files include:
        1. Common Crawl (https://commoncrawl.org)
        2. Internet Archive (https://archive.org)
        3. Custom web crawls using tools like wget or Heritrix
        
        The tool supports various processors that can be applied to the WARC
        records, such as:
        - HTML processing to extract readable text
        - Metadata extraction
        - Content classification
        - Custom processors
        
        Processed records are written to an output file in a configurable format.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'input',
        help='Input WARC file path'
    )
    parser.add_argument(
        'output',
        help='Output file path'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    if args is None:
        args = sys.argv[1:]
        
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None):
    """Main entry point.
    
    Args:
        args: Command line arguments. If None, sys.argv[1:] is used.
    """
    # Parse arguments
    parsed_args = parse_args(args)
    
    # Configure logging
    if parsed_args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
        
    logging.basicConfig(
        level=log_level,
        format='%(levelname)-8s %(name)s:%(filename)s:%(lineno)d %(message)s'
    )
    
    # Create processor chain
    processor = WarcProcessorFactory.create([HtmlProcessor()])
    
    try:
        # Process WARC file
        stats = processor.process_warc_file(parsed_args.input, parsed_args.output)
        
        # Print final stats
        print(f"\nProcessed {stats.records_processed} records")
        print(f"Skipped {stats.records_skipped} records")
        print(f"Failed {stats.records_failed} records")
        
    except Exception as e:
        print(f"Error processing WARC file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
