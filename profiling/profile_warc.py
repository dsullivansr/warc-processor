#!/usr/bin/env python3
"""Profile WARC processing performance."""

import argparse
import cProfile
import pstats
import sys
from typing import Optional, List

from memory_profiler import profile

from warc_processor_main import main


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Profile WARC processing performance')
    parser.add_argument('input', help='Input WARC file path')
    parser.add_argument('output', help='Output file path')
    parser.add_argument('--parser',
                        choices=['html5lib', 'lxml', 'html.parser'],
                        default='html5lib',
                        help='HTML parser to use')
    parser.add_argument('--memory',
                        action='store_true',
                        help='Enable memory profiling')
    parser.add_argument('-v',
                        '--verbose',
                        action='store_true',
                        help='Enable verbose logging')

    if argv is None:
        argv = sys.argv[1:]
    return parser.parse_args(argv)


def run_profiler(options: argparse.Namespace):
    """Run cProfile on WARC processing."""
    # Create profiler
    profiler = cProfile.Profile()

    # Profile the main function
    profiler.enable()
    main_args = [options.input, options.output, '--parser', options.parser]
    if options.verbose:
        main_args.append('-v')
    main(main_args)
    profiler.disable()

    # Print stats sorted by cumulative time
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')

    print("\nTop 20 functions by cumulative time:")
    stats.print_stats(20)

    print("\nTop 20 functions by number of calls:")
    stats.sort_stats('calls')
    stats.print_stats(20)

    # Save profiling data to file
    stats_file = f'profile_{options.parser}.stats'
    stats.dump_stats(stats_file)
    print(f"\nProfiling data saved to {stats_file}")


@profile
def run_memory_profiler(options: argparse.Namespace):
    """Run memory profiler on WARC processing."""
    main_args = [options.input, options.output, '--parser', options.parser]
    if options.verbose:
        main_args.append('-v')
    main(main_args)


def main_profiler():
    """Main entry point for profiling."""
    options = parse_args()

    if options.memory:
        print(f"Running memory profiler with parser: {options.parser}")
        run_memory_profiler(options)
    else:
        print(f"Running cProfile with parser: {options.parser}")
        run_profiler(options)


if __name__ == '__main__':
    main_profiler()
