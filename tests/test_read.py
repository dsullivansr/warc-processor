"""Test reading a WARC file."""

import gzip
import sys


def read_warc_start(warc_path: str) -> None:
    """Read and print the first 1KB of a WARC file."""
    print(f"Attempting to read: {warc_path}")

    try:
        with gzip.open(warc_path, "rb") as f:
            print("File opened successfully")
            data = f.read(1024)
            print(f"Read {len(data)} bytes")
            print("First 100 bytes:")
            print(data[:100])
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except gzip.BadGzipFile as e:
        print(f"Invalid gzip file: {e}")
    except PermissionError as e:
        print(f"Permission denied: {e}")
    except OSError as e:
        print(f"I/O error: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_read.py <warc_file>")
        sys.exit(1)

    read_warc_start(sys.argv[1])
