import argparse
import json
import logging
import sys
from warc_processor_factory import WarcProcessorFactory


def main(args=None):
    """Main function to process WARC files."""
    parser = argparse.ArgumentParser(description="Process WARC files.")
    parser.add_argument("input_files", nargs="+", help="Input WARC files")
    parser.add_argument("--output", help="Output file")
    parser.add_argument("--config", help="Configuration file")

    args = parser.parse_args(args)

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    output_file = args.output

    if not args.input_files:
        print("No input files provided.")
        sys.exit(1)

    with open(args.config, encoding='utf-8') as f:
        config = json.load(f)
    warc_processor = WarcProcessorFactory().create(config)

    for file in args.input_files:
        logging.info("Processing %s", file)
        warc_processor.process(file, output_file)
        try:
            warc_processor.process(file, output_file)
        except (OSError, RuntimeError) as e:
            logging.error("Error processing %s: %s", file, e)


if __name__ == "__main__":
    sys.exit(main())
