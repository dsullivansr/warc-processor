#!/usr/bin/env python3
"""Profile the WARC processor performance."""

import cProfile
import os
import pstats
import sys
import tempfile
from datetime import datetime

from beautiful_soup_html_processor import BeautifulSoupHtmlProcessor
from warc_processor_factory import WarcProcessorFactory


def profile_processor(warc_path: str):
    """Profile the WARC processor.

    Args:
        warc_path: Path to WARC file to process.
    """
    # Create temporary output file
    output_path = tempfile.mktemp()

    # Create processor
    processor = WarcProcessorFactory.create([BeautifulSoupHtmlProcessor()])

    print(f"\nProcessing WARC file: {warc_path}")
    print(f"Output path: {output_path}")

    # Profile processing
    start_time = datetime.now()
    profiler = cProfile.Profile()
    profiler.enable()

    # Process WARC file
    processor.process_warc_file(warc_path, output_path)

    profiler.disable()
    processing_time = datetime.now() - start_time

    # Print results
    print(f"\nProcessing time: {processing_time}")

    # Save profile stats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(50)

    # Clean up
    if os.path.exists(output_path):
        os.remove(output_path)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python profile_processor.py <warc_file>")
        sys.exit(1)

    profile_processor(sys.argv[1])
