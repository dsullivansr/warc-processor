# Release Checklist

## Pre-Release Checks

### Code Quality
- [ ] All tests passing locally
- [ ] Code coverage meets threshold (>80%)
- [ ] No outstanding linting issues
- [ ] Documentation is up to date
- [ ] API documentation generated
- [ ] CHANGELOG.md updated

### Version Update
- [ ] Version bumped in setup.py
- [ ] Version consistent in all files
- [ ] CHANGELOG.md reflects all changes
- [ ] Breaking changes documented

### Dependencies
- [ ] requirements.txt up to date
- [ ] requirements-dev.txt up to date
- [ ] System dependencies documented
- [ ] Compatibility tested with Python 3.12

## Release Process

### Local Testing
- [ ] Clean build environment
- [ ] Binary builds successfully
- [ ] Integration tests pass
- [ ] Performance benchmarks run
- [ ] Manual smoke tests completed

### Release Creation
- [ ] Version committed to main
- [ ] Release tag created
- [ ] Tag pushed to GitHub
- [ ] GitHub Actions workflow started
- [ ] Release notes prepared

### Artifact Verification
- [ ] Binary downloads and runs
- [ ] SHA256 checksums verify
- [ ] Docker image builds and runs
- [ ] Singularity image builds and runs
- [ ] pip installation works

## Post-Release

### Documentation
- [ ] Release notes published
- [ ] Installation guide tested
- [ ] Upgrade guide if needed
- [ ] Known issues documented

### Deployment
- [ ] Container images pushed
- [ ] PyPI package published
- [ ] Release announced
- [ ] Old version deprecation notice (if applicable)

### Cleanup
- [ ] Release branch cleaned up
- [ ] CI/CD pipelines passing
- [ ] Issue tracker updated
- [ ] Project board updated

## Final Verification

### Installation Methods
- [ ] pip install warc-processor==X.Y.Z
- [ ] docker pull warc-processor:X.Y.Z
- [ ] Binary installation
- [ ] Development installation

### Platform Testing
- [ ] Linux x86_64
- [ ] CI environment
- [ ] Cluster deployment
- [ ] Container orchestration

## Release Announcement

### Internal
- [ ] Team notified
- [ ] Documentation updated
- [ ] Support team briefed
- [ ] Migration guides ready

### External
- [ ] Release notes published
- [ ] Blog post (if major release)
- [ ] Social media updates
- [ ] User documentation updated
