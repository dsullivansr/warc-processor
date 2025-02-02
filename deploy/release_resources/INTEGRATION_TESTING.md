# Integration Testing Guide

## Pre-Release Testing

### 1. Environment Setup

```bash
# Create clean test environment
python -m venv test-env
source test-env/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install test utilities
pip install pytest-benchmark pytest-cov pytest-integration
```

### 2. Core Functionality Tests

```bash
# Run full test suite
pytest tests/ --cov=warc_processor

# Run integration tests only
pytest tests/integration/ -v

# Run performance benchmarks
pytest tests/benchmarks/ --benchmark-only
```

### 3. Deployment Tests

#### Binary Distribution
```bash
# Build and test binary
cd deploy/binary
./create_release.sh
cd ../../dist
tar xzf warc-processor-*.tar.gz
./warc-processor-*/warc-processor --version

# Test with sample data
./warc-processor-*/warc-processor --input test_data/sample.warc
```

#### Docker Container
```bash
# Build and test container
cd deploy/containers
docker build -t warc-processor:test .
docker run warc-processor:test --version

# Test with mounted data
docker run -v $(pwd)/test_data:/data warc-processor:test \
    --input /data/sample.warc
```

#### Singularity Container
```bash
# Build and test Singularity image
cd deploy/containers
singularity build test.sif singularity.def
singularity run test.sif --version

# Test with bound data
singularity run --bind test_data:/data test.sif \
    --input /data/sample.warc
```

### 4. Performance Testing

```bash
# CPU profiling
python -m cProfile -o profile.stats warc_processor_main.py

# Memory profiling
mprof run warc_processor_main.py
mprof plot

# Load testing
./load_test.sh  # Custom load test script
```

## Automated Test Matrix

### Python Versions
- [ ] Python 3.12
- [ ] Python 3.11
- [ ] Python 3.10

### Operating Systems
- [ ] Ubuntu Latest
- [ ] CentOS/RHEL
- [ ] Debian

### Deployment Methods
- [ ] pip install
- [ ] Binary installation
- [ ] Docker deployment
- [ ] Singularity deployment
- [ ] Cluster deployment

## Integration Test Scenarios

### 1. Basic Processing
- [ ] Single WARC file processing
- [ ] Multiple WARC file processing
- [ ] Large WARC file handling
- [ ] Error handling and recovery

### 2. Resource Management
- [ ] Memory usage monitoring
- [ ] CPU utilization
- [ ] Disk I/O performance
- [ ] Network usage (if applicable)

### 3. Cluster Integration
- [ ] Job submission
- [ ] Resource allocation
- [ ] Error handling
- [ ] Output collection

### 4. Container Orchestration
- [ ] Container startup
- [ ] Resource limits
- [ ] Volume mounting
- [ ] Network access

## Performance Benchmarks

### Baseline Metrics
- Processing speed (records/second)
- Memory usage per record
- CPU usage patterns
- I/O throughput

### Regression Testing
```bash
# Compare with previous release
pytest-benchmark compare --group-by=func
```

## Security Testing

### 1. Dependency Scanning
```bash
# Check for security vulnerabilities
safety check

# Update dependencies if needed
pip-audit
```

### 2. Container Security
```bash
# Scan Docker image
docker scan warc-processor:test

# Check Singularity permissions
singularity inspect test.sif
```

## Reporting

### Test Results
```bash
# Generate HTML report
pytest --html=report.html

# Generate coverage report
coverage html
```

### Performance Report
```bash
# Generate benchmark report
pytest-benchmark compare --csv=benchmark.csv
python generate_perf_report.py
```

## Continuous Integration

### GitHub Actions
- [ ] Test matrix runs
- [ ] Coverage reports
- [ ] Security scans
- [ ] Performance benchmarks

### Release Validation
- [ ] All tests pass
- [ ] No performance regressions
- [ ] Security checks pass
- [ ] Documentation updated
