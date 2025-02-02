# WARC Processor Deployment Guide

This guide explains different ways to deploy and run the WARC Processor, helping you choose the best option for your use case.

## Deployment Options

### 1. Standalone Binary
**Best for:**
- Single-user deployment
- Systems without Python installed
- Quick deployment without environment setup
- Running on clusters without container support

**How to Deploy:**
```bash
# Build the binary
cd deploy/binary
./create_release.sh

# Copy to target system
scp dist/warc-processor-<version>-linux-x86_64.tar.gz target-system:/desired/path/

# On target system
tar xzf warc-processor-<version>-linux-x86_64.tar.gz
cd warc-processor-<version>-linux-x86_64
chmod +x warc-processor
./warc-processor [arguments]
```

### 2. Docker Container
**Best for:**
- Development environments
- CI/CD pipelines
- Microservice deployments
- Environments with Docker support

**How to Deploy:**
```bash
# Build the container
cd deploy/containers
docker build -t warc-processor .

# Run the container
docker run -v /path/to/data:/data warc-processor \
    --input /data/input.warc \
    --output /data/output

# Or push to a registry
docker tag warc-processor your-registry/warc-processor:version
docker push your-registry/warc-processor:version
```

### 3. Singularity Container
**Best for:**
- HPC environments
- Scientific computing clusters
- Secure environments where Docker isn't allowed
- Multi-user systems

**How to Deploy:**
```bash
# Build the container
cd deploy/containers
singularity build warc-processor.sif singularity.def

# Copy to cluster
scp warc-processor.sif cluster:/path/to/work/

# Run directly
singularity run \
    --bind /path/to/data:/data \
    warc-processor.sif \
    --input /data/input.warc \
    --output /data/output

# Or via Slurm
cd deploy/cluster
sbatch slurm_job.sh
```

### 4. Cluster Job (Slurm)
**Best for:**
- Processing large WARC files
- Batch processing multiple files
- Utilizing cluster resources
- Long-running jobs

**How to Deploy:**
```bash
# 1. Using Singularity container (recommended)
cd deploy/cluster
# Edit slurm_job.sh to set your paths and parameters
sbatch slurm_job.sh

# 2. Using Python virtual environment
python -m venv ~/.venv/warc
source ~/.venv/warc/bin/activate
pip install -r requirements.txt

# Then submit job
sbatch slurm_job.sh
```

## Choosing the Right Deployment Method

1. **Use Binary Distribution if:**
   - You need a simple, standalone solution
   - Target system doesn't have Python
   - You want minimal setup
   - You're running on a basic Linux system

2. **Use Docker if:**
   - You're running in a cloud environment
   - You need reproducible environments
   - You're integrating with CI/CD
   - You're comfortable with Docker

3. **Use Singularity if:**
   - You're working on an HPC system
   - You need container security
   - You're running on a shared cluster
   - Docker isn't available

4. **Use Cluster Deployment if:**
   - You have large-scale processing needs
   - You need to utilize HPC resources
   - You're processing multiple files
   - You need job scheduling

## Additional Resources

Each deployment method has its own directory with specific configurations:
- `/binary` - Standalone executable creation
- `/containers` - Docker and Singularity definitions
- `/cluster` - Cluster job configurations
- `/scripts` - Automation scripts

## Troubleshooting

If you encounter issues:
1. Check the logs in the respective output files
2. Ensure all paths are correctly set
3. Verify system requirements are met
4. For cluster jobs, check the job scheduler output

For more detailed information about each deployment method, see the README files in their respective directories.
