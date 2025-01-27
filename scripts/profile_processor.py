#!/usr/bin/env python3
"""Profile the WARC processor performance."""

import cProfile
import pstats
from pstats import SortKey

from warc_processor import WarcProcessor
from warc_record_parser import WarcRecordParser
from warc_record_processor_chain import WarcRecordProcessorChain
from html_processor import HtmlProcessor
from plain_text_writer import PlainTextWriter
from processing_stats import ProcessingStats


def main():
    """Run profiling on WARC processor."""
    # Initialize components
    record_parser = WarcRecordParser()
    html_processor = HtmlProcessor()
    processors = [html_processor]
    processor_chain = WarcRecordProcessorChain(processors)
    output_writer = PlainTextWriter()
    stats = ProcessingStats()

    # Create processor
    processor = WarcProcessor(processors=processors,
                              output_writer=output_writer,
                              record_parser=record_parser,
                              stats=stats,
                              processor_chain=processor_chain)

    # Profile processing
    profiler = cProfile.Profile()
    profiler.enable()

    # Process sample file
    warc_path = ('/data01/commoncrawl/crawl-data/CC-NEWS/2024/12/'
                 'CC-NEWS-20241231224228-00155.warc.gz')
    processor.process_warc_file(warc_path, 'test_data/full_output.txt')

    profiler.disable()

    # Print stats sorted by cumulative time
    stats = pstats.Stats(profiler).sort_stats(SortKey.CUMULATIVE)
    stats.print_stats(30)  # Show top 30 entries


if __name__ == '__main__':
    main()
