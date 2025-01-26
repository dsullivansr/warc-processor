"""Create a test WARC file."""

import os
import sys
from datetime import datetime, UTC
from io import BytesIO
from warcio.warcwriter import WARCWriter
from warcio.statusandheaders import StatusAndHeaders

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create test WARC file
with open('test_data/sample.warc', 'wb') as output:
    writer = WARCWriter(output, gzip=False)

    # Create response record
    headers_list = [
        ('Content-Type', 'text/html'),
        ('Content-Length', '156'),
    ]

    http_headers = StatusAndHeaders('200 OK', headers_list, protocol='HTTP/1.1')

    payload = b'''<html>
<head><title>Test Page</title></head>
<body>
<h1>Hello World</h1>
<p>This is a test page.</p>
</body>
</html>
'''

    warc_headers = {
        'WARC-Type': 'response',
        'WARC-Record-ID': '<urn:uuid:test-id>',
        'WARC-Date': datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'WARC-Target-URI': 'http://example.com',
        'Content-Type': 'text/html',
    }

    record = writer.create_warc_record('http://example.com',
                                       'response',
                                       payload=BytesIO(payload),
                                       http_headers=http_headers,
                                       warc_headers_dict=warc_headers)

    writer.write_record(record)
