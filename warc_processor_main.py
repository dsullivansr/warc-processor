"""Main script for processing WARC files."""

import argparse
import logging
import os
import sys

from warc_processor_factory import WarcProcessorFactory


def parse_args():
    """Parse command line arguments.

    Returns:
        Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="Process WARC files")

    parser.add_argument(
        "input", help="Input WARC file or directory containing WARC files"
    )

    parser.add_argument(
        "--output", "-o", help="Output file or directory", required=True
    )

    parser.add_argument(
        "--parser",
        choices=["html5lib", "lxml", "html.parser"],
        default="html5lib",
        help="HTML parser to use (default: html5lib)",
    )

    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to YAML configuration file (default: config.yaml)",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )

    return parser.parse_args()


def main():
    """Main entry point.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    args = parse_args()

    # Configure logging
    logging.basicConfig(level=getattr(logging, args.log_level))
    logger = logging.getLogger(__name__)

    # Check if input exists
    if not os.path.exists(args.input):
        logger.error("Input path not found: %s", args.input)
        return 1

    # Check if config exists
    if not os.path.exists(args.config):
        logger.error("Config file not found: %s", args.config)
        return 1

    try:
        # Create processor using default configuration as dynamic config loading is removed
        processor = WarcProcessorFactory.create(processors=[])

        # Process input path
        if os.path.isfile(args.input):
            processor.process_warc_file(args.input, args.output)
        else:
            for root, _, files in os.walk(args.input):
                for file in files:
                    if file.endswith(".warc") or file.endswith(".warc.gz"):
                        input_path = os.path.join(root, file)
                        output_path = os.path.join(args.output, file + ".txt")
                        processor.process_warc_file(input_path, output_path)

        return 0

    except Exception as e:
        logger.error("Failed to create processor: %s", str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
