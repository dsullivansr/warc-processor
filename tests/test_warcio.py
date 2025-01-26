"""Test reading a WARC file using warcio."""

import sys
from warcio.archiveiterator import ArchiveIterator


def process_warc(warc_path: str) -> None:
    """Process a WARC file and print info about each record."""
    print(f"Processing: {warc_path}")

    try:
        with open(warc_path, 'rb') as stream:
            for record in ArchiveIterator(stream):
                print("\nRecord:")
                print(f"Type: {record.rec_type}")
                print(f"Headers: {record.rec_headers}")
                if record.rec_type == 'response':
                    print("Content:")
                    content = record.content_stream().read()
                    print(f"Length: {len(content)} bytes")
                    print(f"First 200 bytes: {content[:200]}")
                    break  # Just process one response record as a test

    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python test_warcio.py <warc_file>")
        sys.exit(1)

    process_warc(sys.argv[1])
