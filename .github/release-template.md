# WARC Processor ${VERSION}

## What's New
${CHANGES}

## Installation Options

### Binary Installation
```bash
# Download and verify
wget https://github.com/dsullivansr/warc-processor/releases/download/${VERSION}/warc-processor-*.tar.gz
wget https://github.com/dsullivansr/warc-processor/releases/download/${VERSION}/SHA256SUMS
sha256sum -c SHA256SUMS

# Install
tar xzf warc-processor-*.tar.gz
cd warc-processor-*
./warc-processor [arguments]
```

### Container Installation
```bash
# Docker
docker pull ghcr.io/dsullivansr/warc-processor:${VERSION}

# Singularity
singularity pull warc-processor.sif docker://ghcr.io/dsullivansr/warc-processor:${VERSION}
```

### Pip Installation
```bash
pip install warc-processor==${VERSION#v}
```

## Documentation
For detailed deployment options and instructions, see the [deployment guide](deploy/README.md).

## SHA256 Checksums
```
${CHECKSUMS}
```
