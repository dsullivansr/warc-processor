# WARC Processor

A Python library for processing WARC (Web ARChive) files with support for custom content processors. This tool is particularly useful for extracting and processing content from web crawl archives.

## Features

- Process WARC files with custom content processors
- Built-in HTML content processor
- Support for gzipped WARC files
- Robust encoding handling
- Extensible processor interface
- Detailed processing statistics
  - Track parsed, processed, skipped, and failed records
  - Monitor file sizes and processing progress
- Progress tracking and error handling

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/warc-processor.git
cd warc-processor
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package and its dependencies:
```bash
pip install -e .
pip install warcio beautifulsoup4 html5lib
```

## Usage

### Command Line Interface

The simplest way to use the WARC processor is through its command-line interface:

```bash
python warc_processor_main.py [-v] input.warc.gz output.txt
```

Options:
- `input.warc.gz`: Path to input WARC file (can be .warc or .warc.gz)
- `output.txt`: Path where the processed output should be written
- `-v, --verbose`: Enable verbose logging for debugging

Example:
```bash
python warc_processor_main.py crawl.warc.gz extracted_text.txt
```

### Processing Statistics

The processor tracks detailed statistics about the processing run:

- `records_parsed`: Number of records successfully parsed from the WARC file
- `records_processed`: Number of records successfully processed
- `records_skipped`: Number of records skipped (e.g., non-HTML content)
- `records_failed`: Number of records that failed during processing
- `input_size`: Size of input WARC file in bytes
- `input_size_mb`: Size of input WARC file in megabytes

These statistics are available both programmatically and in the command-line output.

### Python API

For more control over the processing, you can use the Python API:

```python
from html_processor import HtmlProcessor
from plain_text_writer import PlainTextWriter
from warc_processor import WarcProcessor
from warc_record_parser import WarcRecordParser
from warc_record_processor_chain import WarcRecordProcessorChain
from processing_stats import ProcessingStats

# Create components
processors = [HtmlProcessor()]
processor_chain = WarcRecordProcessorChain(processors)
record_parser = WarcRecordParser()
stats = ProcessingStats()
output_writer = PlainTextWriter()

# Create processor
processor = WarcProcessor(
    processors=processors,
    output_writer=output_writer,
    record_parser=record_parser,
    stats=stats,
    processor_chain=processor_chain
)

# Process file
stats = processor.process_warc_file('input.warc.gz', 'output.txt')

# Access processing statistics
print(f"Parsed records: {stats.records_parsed}")
print(f"Processed records: {stats.records_processed}")
print(f"Skipped records: {stats.records_skipped}")
print(f"Failed records: {stats.records_failed}")
```

### Custom Processors

You can create custom processors by implementing the `WarcRecordProcessor` interface:

```python
from warc_record_processor import WarcRecordProcessor
from models.warc_record import WarcRecord
from typing import Optional

class MyProcessor(WarcRecordProcessor):
    def can_process(self, record: WarcRecord) -> bool:
        """Return True if this processor can handle the record."""
        return record.content_type == 'my/content-type'
        
    def process(self, record: WarcRecord) -> Optional[str]:
        """Process the record content.
        
        Returns:
            Processed content as string if successful, None if skipped.
        """
        try:
            # Process the record content
            return process_content(record.content)
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return None
```

## Getting WARC Files

You can obtain WARC files from several sources:

1. Common Crawl: https://commoncrawl.org/the-data/get-started/
   ```bash
   # Example: Download a small WARC file from Common Crawl
   wget https://data.commoncrawl.org/crawl-data/CC-MAIN-2024-04/segments/1704876185753.97/warc/CC-MAIN-20240110091500-20240110121500-00000.warc.gz
   ```

2. Internet Archive: https://archive.org/
   - Many collections are available in WARC format

3. Create your own using wget:
   ```bash
   wget --warc-file=my-crawl http://example.com
   ```

## Development

Run tests:
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=.
```

## Error Handling

The processor handles several types of errors:
- FileNotFoundError: If input WARC file doesn't exist
- PermissionError: If output path isn't writable
- ValueError: If processor chain fails
- Various parsing and processing errors are logged but don't stop processing

Enable verbose logging with `-v` to see detailed error messages.

## License

MIT License
