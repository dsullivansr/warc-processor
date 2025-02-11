import argparse
import logging
import os
import sys
from warc_processor_factory import WarcProcessorFactory


def main(args=None):
    """Main function to process WARC files."""
    parser = argparse.ArgumentParser(description="Process WARC files.")
    parser.add_argument("--input", required=True, help="Input WARC file")

    args = parser.parse_args(args)

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    input_file = args.input
    if not input_file:
        print("No input file provided.")
        sys.exit(1)

    try:
        warc_processor = WarcProcessorFactory().create()
        # Create output path by appending .txt to input file
        output_file = input_file + '.txt'
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        warc_processor.process_warc_file(input_file, output_file)
        return 0
    except (OSError, RuntimeError) as e:
        logging.error("Error processing %s: %s", input_file, e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
