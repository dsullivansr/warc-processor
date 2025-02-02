# Container Deployments

This directory contains container definitions for Docker and Singularity/Apptainer deployments.

## Docker

### Basic Usage
```bash
# Build
docker build -t warc-processor .

# Run
docker run -v /path/to/data:/data warc-processor \
    --input /data/input.warc \
    --output /data/output
```

### Dockerfile Customization

The Dockerfile uses multi-stage builds for smaller images:
```dockerfile
# Build stage
FROM python:3.12-slim as builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.12-slim
COPY --from=builder /root/.local /root/.local
```

### Environment Variables
```bash
# Configure at runtime
docker run -e MAX_MEMORY=4G -e THREADS=4 warc-processor

# Or in docker-compose.yml
version: '3'
services:
  warc-processor:
    build: .
    environment:
      - MAX_MEMORY=4G
      - THREADS=4
    volumes:
      - ./data:/data
```

## Singularity/Apptainer

### Basic Usage
```bash
# Build
singularity build warc-processor.sif singularity.def

# Run
singularity run --bind /path/to/data:/data warc-processor.sif \
    --input /data/input.warc \
    --output /data/output
```

### Definition File Customization

```singularity
# Use specific Python version
Bootstrap: docker
From: python:3.12-slim

# Add system packages
%post
    apt-get update && apt-get install -y \
        package1 \
        package2

# Set environment variables
%environment
    export MAX_MEMORY=4G
    export THREADS=4

# Custom entrypoint
%runscript
    exec python /opt/warc-processor/warc_processor_main.py "$@"
```

### Bind Mounts
```bash
# Multiple bind mounts
singularity run \
    --bind /data:/data \
    --bind /scratch:/scratch \
    warc-processor.sif

# Bind with read-only
singularity run \
    --bind /data:/data:ro \
    warc-processor.sif
```

## Performance Tuning

### Docker
1. Use multi-stage builds
2. Minimize layer count
3. Use `.dockerignore`
4. Consider `alpine` base for smaller images

### Singularity
1. Use `%files` for copying
2. Leverage bind mounts
3. Use `--contain` for isolation
4. Consider using `--nv` for GPU support

## Resource Management

### Docker
```bash
# Limit resources
docker run \
    --memory=4g \
    --cpus=2 \
    warc-processor
```

### Singularity
```bash
# Use cgroups (if available)
singularity run \
    --apply-cgroups resources.conf \
    warc-processor.sif
```

## Integration with Cluster

See `../cluster/README.md` for running containers in cluster environments.
