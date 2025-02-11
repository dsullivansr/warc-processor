import argparse
import logging
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
        warc_processor.process(input_file)
        return 0
    except (OSError, RuntimeError) as e:
        logging.error("Error processing %s: %s", input_file, e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
