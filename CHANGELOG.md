# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-01-25

### Added
- New records_parsed metric to track number of successfully parsed records
- Improved record tracking accuracy in processing statistics

### Changed
- Updated code style to comply with Google Python Style Guide
- Removed unused tools directory

## [0.1.0] - 2025-01-25

### Added
- Initial release of WARC Processor
- Basic WARC file processing functionality
- HTML content processor
- Plain text output writer
- Command-line interface
- Extensible processor interface
- Processing statistics tracking
- Comprehensive documentation
- Test suite with high coverage

### Dependencies
- Python 3.7+
- warcio 1.7.4
- beautifulsoup4 4.12.3
- pytest 8.0.0 (development)
- pytest-cov 4.1.0 (development)
