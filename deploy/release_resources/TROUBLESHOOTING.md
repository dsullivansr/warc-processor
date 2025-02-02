# Release Troubleshooting Guide

## Common Issues and Solutions

### 1. Binary Build Failures

#### PyInstaller Import Errors
```
ERROR: Cannot find module 'some_module'
```
**Solution:**
1. Add to hidden imports in spec file:
   ```python
   hiddenimports=['some_module']
   ```
2. Verify module is in requirements.txt
3. Test with: `python -c "import some_module"`

#### Missing Dependencies
```
error while loading shared libraries: libxyz.so
```
**Solution:**
1. Install system package: `apt-get install libxyz-dev`
2. Add to Dockerfile/singularity.def
3. Document in deployment guide

### 2. GitHub Actions Issues

#### Workflow Permission Errors
```
Resource not accessible by integration
```
**Solution:**
1. Check repository settings
2. Enable "Read and write permissions" in Actions
3. Verify GITHUB_TOKEN permissions

#### Build Artifact Too Large
```
Error: Artifact too large
```
**Solution:**
1. Use UPX compression in PyInstaller
2. Split artifacts if needed
3. Use release assets instead of artifacts

### 3. Version Conflicts

#### Git Tag Exists
```
fatal: tag 'v1.0.0' already exists
```
**Solution:**
1. Verify version bump in setup.py
2. Delete tag if incorrect: `git tag -d v1.0.0`
3. Force push if needed: `git push --delete origin v1.0.0`

#### Version Mismatch
```
Version in setup.py doesn't match tag
```
**Solution:**
1. Update setup.py version
2. Update CHANGELOG.md
3. Create new commit before tagging

### 4. Container Build Issues

#### Layer Caching Problems
```
Step 14/15 : RUN pip install ...
ERROR: Cache miss
```
**Solution:**
1. Clear GitHub Actions cache
2. Optimize Dockerfile layers
3. Use multi-stage builds

#### Registry Authentication
```
Error: denied: permission_denied
```
**Solution:**
1. Check registry credentials
2. Verify GitHub secrets
3. Test locally: `docker login ghcr.io`

## Integration Testing Problems

### Failed Integration Tests
```
Error: Test suite failed
```
**Solution:**
1. Run tests locally first
2. Check test environment variables
3. Verify test data availability

### Performance Regression
```
Warning: Performance threshold exceeded
```
**Solution:**
1. Run benchmarks locally
2. Compare with previous release
3. Document if expected change
