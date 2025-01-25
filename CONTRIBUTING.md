# Contributing to WARC Processor

We love your input! We want to make contributing to WARC Processor as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

## Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install development dependencies:
```bash
pip install -e ".[dev]"
```

3. Run tests:
```bash
python -m pytest
```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to all public functions and classes
- Include type hints where appropriate
- Keep functions focused and concise

## Testing

- Write unit tests for new functionality
- Maintain or improve test coverage
- Test edge cases and error conditions
- Use descriptive test names

## Documentation

- Update README.md with any new features
- Document new functions and classes
- Keep API documentation up to date
- Add examples for complex features

## License

By contributing, you agree that your contributions will be licensed under its MIT License.

## References

- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Type Hints Documentation](https://docs.python.org/3/library/typing.html)
- [WARC Format Specification](https://iipc.github.io/warc-specifications/specifications/warc-format/warc-1.1/)
