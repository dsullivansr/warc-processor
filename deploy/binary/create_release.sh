#!/bin/bash
set -e

# Get version from setup.py or default to date-based version
VERSION=$(python3 -c "exec(open('setup.py').read()); print(__version__)" 2>/dev/null || date +"%Y.%m.%d")
RELEASE_NAME="warc-processor-${VERSION}-linux-x86_64"
RELEASE_DIR="dist/${RELEASE_NAME}"

# Clean previous builds
rm -rf build dist/*

# Create release directory structure
mkdir -p "${RELEASE_DIR}"

# Build binary using PyInstaller
python3 -m PyInstaller --onefile \
    --name warc-processor \
    --add-data "config.yaml:." \
    warc_processor_main.py

# Copy necessary files
cp dist/warc-processor "${RELEASE_DIR}/"
cp config.yaml "${RELEASE_DIR}/"
cp README.md "${RELEASE_DIR}/"
cp LICENSE "${RELEASE_DIR}/"

# Create quick start guide
cat > "${RELEASE_DIR}/QUICKSTART.md" << 'EOF'
# WARC Processor Quick Start Guide

This is a standalone binary release of the WARC Processor tool.

## Usage

1. Make the binary executable:
   ```bash
   chmod +x warc-processor
   ```

2. Run the processor:
   ```bash
   ./warc-processor [arguments]
   ```

The binary includes all necessary dependencies and does not require Python to be installed.

For full documentation, please see README.md
EOF

# Create archive
cd dist
tar czf "${RELEASE_NAME}.tar.gz" "${RELEASE_NAME}"
rm -rf "${RELEASE_NAME}"

echo "Created release archive: dist/${RELEASE_NAME}.tar.gz"
