import argparse
import logging
import os
import sys
from warc_processor_factory import WarcProcessorFactory
from warc_processor_types import OutputWriters, RecordProcessors


def main(args=None):
    """Main function to process WARC files."""
    parser = argparse.ArgumentParser(description="Process WARC files.")
    parser.add_argument(
        "--input",
        required=True,
        help="Input WARC file"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file for processed content"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output file if it exists"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--processor",
        choices=[
            "lexbor",
            "beautiful_soup_lxml",
            "beautiful_soup_html5",
            "beautiful_soup_builtin"
        ],
        default="lexbor",
        help="HTML processor to use (default: lexbor)"
    )

    args = parser.parse_args(args)

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    try:
        warc_processor = WarcProcessorFactory().create(
            output_writer=OutputWriters[args.format.upper()],
            processors=RecordProcessors[args.processor.upper()]
        )

        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        warc_processor.process_warc_file(
            args.input, args.output, overwrite=args.overwrite
        )
        return 0
    except (OSError, RuntimeError) as e:
        logging.error("Error processing %s: %s", args.input, e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
