#!/usr/bin/env python3
"""Read WARC file and count records."""

import gzip
import time
from warcio.archiveiterator import ArchiveIterator


def read_warc():
    """Read WARC file and count records."""
    input_path = ('/data01/commoncrawl/crawl-data/CC-NEWS/2024/12/'
                  'CC-NEWS-20241231224228-00155.warc.gz')

    records = 0
    bytes_read = 0
    start = time.time()

    with gzip.open(input_path, 'rb') as f:
        for record in ArchiveIterator(f):
            if record.rec_type == 'response':
                records += 1
                # Read content to /dev/null
                content_stream = record.content_stream()
                while True:
                    chunk = content_stream.read(8192)
                    if not chunk:
                        break
                    bytes_read += len(chunk)

    end = time.time()
    duration = end - start
    print(f"Read {records} records in {duration:.2f} seconds")
    print(f"Total bytes read: {bytes_read/1024/1024:.2f}MB")
    print(f"Average time per record: {(duration/records)*1000:.2f}ms")
    print(f"Average bytes per record: {bytes_read/records/1024:.2f}KB")


if __name__ == '__main__':
    read_warc()
