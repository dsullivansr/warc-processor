# WARC Processor Project TODOs

## Project Structure Improvements

### Module Organization
- [ ] Create a `core` or `processors` package for WARC processing modules
  - Move `warc_processor.py`, `warc_processor_factory.py`, `warc_record_parser.py` into package
- [ ] Create dedicated packages for different components:
  - `processors/` for processing implementations (e.g., `html_processor.py`)
  - `writers/` for output writer implementations (e.g., `plain_text_writer.py`)

### Models Package
- [ ] Review model-related functionality to ensure clean separation from processing logic
- [ ] Consider creating model interfaces/protocols for better type safety

### Testing Structure
- [ ] Organize test files to mirror main package structure
- [ ] Add integration tests directory for cross-module testing
- [ ] Document test categories and their purposes

### Tools Directory
- [ ] Clarify purpose of tools directory
- [ ] Consider renaming to `scripts` or `utilities` if appropriate
- [ ] Add documentation for each tool

### Documentation
- [ ] Add comprehensive API documentation
- [ ] Create architecture/design documentation
  - System overview
  - Component interactions
  - Data flow diagrams
- [ ] Write developer setup guide
- [ ] Add contribution guidelines
- [ ] Document testing strategy

### Configuration
- [ ] Create dedicated `config` directory
- [ ] Implement configuration management
  - Environment variables
  - Configuration files
  - Default settings
- [ ] Document configuration options

### Entry Points
- [ ] Consider consolidating entry points
- [ ] Move entry point scripts to dedicated `bin` or `cmd` directory
- [ ] Document each entry point's purpose and usage

### Package Structure
- [ ] Implement hierarchical package structure:
```
warc_processor/
├── core/
│   ├── processor.py
│   ├── parser.py
│   └── factory.py
├── processors/
│   └── html_processor.py
├── writers/
│   └── plain_text_writer.py
├── models/
│   └── ...
└── utils/
    └── ...
```

### Dependencies
- [ ] Split requirements.txt into:
  - `requirements.txt` (core dependencies)
  - `requirements-dev.txt` (development dependencies)
  - `requirements-test.txt` (testing dependencies)
- [ ] Add version pins for all dependencies
- [ ] Document dependency management process

### Code Style
- [ ] Review and standardize module naming conventions
- [ ] Add code style documentation
- [ ] Consider adding code formatting tools (e.g., black, isort)
- [ ] Add pre-commit hooks for code style checks

### Error Handling
- [ ] Create dedicated `exceptions.py` module
- [ ] Implement consistent error handling strategy
- [ ] Document error handling patterns
- [ ] Add error recovery procedures

### Interfaces
- [ ] Create explicit interface definitions for processors
- [ ] Document interface contracts
- [ ] Add type hints and runtime checks for interfaces
- [ ] Consider using Protocol classes for structural typing

## Test Coverage Improvements

Current overall test coverage: 86%

### High Priority

1. `processing_stats.py` (68% coverage)
   - Add tests for error tracking methods
   - Add tests for utility methods
   - Missing coverage in lines: 60, 65, 95, 122, 133-137, 145-171

2. `warc_processor_main.py` (67% coverage)
   - Add tests for directory processing functionality
   - Add tests for error handling paths
   - Missing coverage in lines: 68-73, 77-82, 86

3. `tests/test_processor.py` (28% coverage)
   - Major overhaul needed
   - Add tests for lines 25-75, 84-89, 94
   - Consider splitting into multiple test files if needed

### Medium Priority

4. `lexbor_html_processor.py` (84% coverage)
   - Add tests for error handling paths
   - Missing coverage in lines: 30, 59, 102-108

### Low Priority

5. Clean up unused test files
   - `tests/test_read.py` (17% coverage)
   - `tests/test_warcio.py` (17% coverage)
   - Consider removing if no longer needed

## Code TODOs

### Refactoring Opportunities
- [ ] Consider refactoring WarcRecord to reduce number of instance attributes, possibly by grouping related fields into nested structures
- [ ] Consider refactoring WarcProcessor to reduce constructor arguments by having WarcProcessor create its own processor_chain from processors
- [ ] Consider refactoring WarcRecordParser.parse method to reduce number of local variables and complexity
- [ ] Consider extracting common record creation code from WarcRecordParser into a shared utility (trade-off: increased complexity vs reduced duplication)
- [ ] Consider moving common WARC record creation code into a shared utility.
- [ ] HTML Processor should be BeautifulSoupHtmlProcessor (or similar)

### Testing Improvements
- [ ] Consider refactoring TestWarcProcessor to use a fixture object that encapsulates mock objects and temporary files
- [ ] Consider creating test_utils.py with common WARC test data (trade-off: test independence vs code duplication)

## Next Steps
1. Prioritize these improvements based on:
   - Impact on maintainability
   - Development velocity
   - New feature requirements
2. Create GitHub issues for tracking
3. Update documentation as changes are made
4. Maintain test coverage throughout refactoring
