"""Test script for WARC processing."""

import os
import sys
import logging
from processors.beautiful_soup_html_processor import BeautifulSoupHtmlProcessor
from writers.plain_text_writer import PlainTextWriter
from processing_stats import ProcessingStats
from warc_processor import WarcProcessor
from warc_record_parser import WarcRecordParser

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python test_processor.py <warc_file>")
        sys.exit(1)

    warc_path = sys.argv[1]
    if not os.path.exists(warc_path):
        logger.error("File not found: %s", warc_path)
        sys.exit(1)

    logger.info("Processing WARC file: %s", warc_path)
    logger.info("File size: %.2f MB",
                os.path.getsize(warc_path) / (1024 * 1024))

    # Create output path in same directory as input
    output_path = os.path.join(os.path.dirname(warc_path),
                               os.path.basename(warc_path) + '.processed.txt')

    # Create processor components
    html_processor = BeautifulSoupHtmlProcessor()
    output_writer = PlainTextWriter()
    record_parser = WarcRecordParser()
    stats = ProcessingStats()

    # Create processor with HTML handler
    processor = WarcProcessor(processors=[html_processor],
                              output_writer=output_writer,
                              record_parser=record_parser,
                              stats=stats)

    try:
        # Process the file
        logger.info("Starting processing...")
        stats = processor.process_warc_file(warc_path, output_path)

        # Print results
        logger.info("Processing complete!")
        logger.info("Output written to: %s", output_path)
        logger.info("Statistics:")
        log_stats(stats)

    except FileNotFoundError:
        logger.error("Input file not found: %s", warc_path)
        sys.exit(1)
    except IOError as e:
        logger.error("I/O error processing file: %s", e)
        sys.exit(1)
    except ValueError as e:
        logger.error("Invalid WARC file: %s", e)
        sys.exit(1)


def log_stats(stats: ProcessingStats) -> None:
    """Log processing statistics.

    Args:
        stats: Processing statistics.
    """
    logger.info("Records parsed: %d", stats.records_parsed)
    logger.info("Records processed: %d", stats.records_processed)
    logger.info("Records skipped: %d", stats.records_skipped)
    logger.info("Bytes processed: %d", stats.bytes_processed)
    processing_time = stats.get_processing_time()
    logger.info("Processing time: %.2f seconds",
                processing_time.total_seconds())


if __name__ == '__main__':
    main()
