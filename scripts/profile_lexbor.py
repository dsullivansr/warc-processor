#!/usr/bin/env python3
"""Profile the Lexbor HTML processor."""

import cProfile
import pstats
import gzip
import os
from warcio.archiveiterator import ArchiveIterator

from warc_record_parser import WarcRecordParser
from lexbor_html_processor import LexborHtmlProcessor


def profile_lexbor():
    """Profile Lexbor HTML processor on a single WARC file."""
    input_path = ('/data01/commoncrawl/crawl-data/CC-NEWS/2024/12/'
                  'CC-NEWS-20241231224228-00155.warc.gz')

    # Create processor components
    record_parser = WarcRecordParser()
    html_processor = LexborHtmlProcessor()

    # Process records
    records_processed = 0

    with gzip.open(input_path, 'rb') as f:
        for record in ArchiveIterator(f):
            if record.rec_type == 'response':
                try:
                    # Parse record
                    warc_record = record_parser.parse(record)
                    if not warc_record:
                        continue

                    # Process record with profiling
                    html_processor.process(warc_record)
                    records_processed += 1

                except (ValueError, AttributeError) as e:
                    print(f"Error processing record: {str(e)[:80]}")
                    continue

    print(f"\nProcessed {records_processed} records")


if __name__ == '__main__':
    # Create profile output directory
    os.makedirs('profiling', exist_ok=True)

    # Run profiler
    profile_output = 'profiling/lexbor_profile.stats'
    cProfile.run('profile_lexbor()', profile_output)

    # Print stats
    stats = pstats.Stats(profile_output)
    stats.sort_stats('cumulative')

    print("\nTop 20 functions by cumulative time:")
    stats.print_stats(20)

    print("\nTime spent in Lexbor functions:")
    stats.print_stats('lexbor')
