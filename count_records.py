#!/usr/bin/env python3

from warcio.archiveiterator import ArchiveIterator

count_response = 0
count_request = 0

with open('tests/fixtures/sample_recompressed.warc.gz', 'rb') as f:
    for record in ArchiveIterator(f):
        if record.rec_type == 'response':
            count_response += 1
        elif record.rec_type == 'request':
            count_request += 1

print(f'Response records: {count_response}')
print(f'Request records: {count_request}')
