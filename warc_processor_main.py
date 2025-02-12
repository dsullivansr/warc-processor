import argparse
import logging
import os
import sys
from warc_processor_factory import WarcProcessorFactory
from models.component_types import OutputWriters, RecordProcessors


def main(args=None):
    """Main function to process WARC files."""
    parser = argparse.ArgumentParser(
        description=(
            "Process WARC (Web ARChive) files by extracting text "
            "content from HTML."
        )
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input WARC file to process"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output file where processed content will be written"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="If set, will overwrite the output file if it already exists"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help=(
            "Output format:\n"
            "  - text: writes plain text with YAML separators (---)\n"
            "  - json: writes as JSON with full metadata\n"
            "(default: text)"
        )
    )
    parser.add_argument(
        "--processor",
        choices=[
            "lexbor",                # Fast C-based HTML parser
            "beautiful_soup_lxml",   # BeautifulSoup with lxml (fast)
            "beautiful_soup_html5",  # BeautifulSoup with html5lib (lenient)
            "beautiful_soup_builtin" # BeautifulSoup with built-in parser
        ],
        default="lexbor",
        help="HTML processor to use. Options:\n"
             "  - lexbor: Fast C-based HTML parser (default)\n"
             "  - beautiful_soup_lxml: BS4 with lxml backend (fast)\n"
             "  - beautiful_soup_html5: BS4 with html5lib "
             "(slow but handles invalid HTML)\n"
             "  - beautiful_soup_builtin: BS4 with Python's built-in parser"
    )

    args = parser.parse_args(args)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
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
