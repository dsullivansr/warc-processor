# Cluster Deployment

This directory contains configurations and scripts for running WARC Processor on HPC clusters.

## Slurm Configuration

### Basic Job Script
```bash
#!/bin/bash
#SBATCH --job-name=warc-process
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=24:00:00
```

### Array Jobs
Process multiple WARC files in parallel:
```bash
#!/bin/bash
#SBATCH --array=0-99
#SBATCH --job-name=warc-array

FILES=($(ls /data/warcs/*.warc))
FILE=${FILES[$SLURM_ARRAY_TASK_ID]}

singularity run \
    --bind /data:/data \
    /path/to/warc-processor.sif \
    --input "$FILE" \
    --output "/data/output/${SLURM_ARRAY_TASK_ID}"
```

### GPU Support
```bash
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu

singularity run --nv warc-processor.sif
```

## Deployment Methods

### 1. Singularity Container (Recommended)
```bash
# Copy container
scp ../containers/warc-processor.sif cluster:/path/

# Submit job
sbatch slurm_job.sh
```

### 2. Virtual Environment
```bash
# Setup environment
module load python/3.12
python -m venv ~/.venv/warc
source ~/.venv/warc/bin/activate
pip install -r ../../requirements.txt

# Submit job
sbatch venv_job.sh
```

### 3. Binary Distribution
```bash
# Copy binary
scp ../binary/dist/warc-processor-*.tar.gz cluster:/path/

# Submit job
sbatch binary_job.sh
```

## Resource Optimization

### Memory Usage
```bash
#SBATCH --mem=16G
#SBATCH --mem-per-cpu=4G
```

### CPU Allocation
```bash
#SBATCH --cpus-per-task=4  # Threading
#SBATCH --nodes=2          # Multiple nodes
#SBATCH --ntasks=4         # MPI tasks
```

### Storage
```bash
#SBATCH --tmp=100G  # Local scratch space
```

## Monitoring and Management

### Job Status
```bash
squeue -u $USER
scontrol show job <jobid>
```

### Resource Usage
```bash
sacct -j <jobid> --format=JobID,JobName,MaxRSS,Elapsed
```

### Job Dependencies
```bash
sbatch --dependency=afterok:<jobid> next_job.sh
```

## Error Handling

1. **Out of Memory**
   ```bash
   #SBATCH --mem=32G  # Increase memory
   ```

2. **Timeout**
   ```bash
   #SBATCH --time=48:00:00  # Increase time limit
   ```

3. **Node Failure**
   ```bash
   #SBATCH --requeue  # Allow job requeue
   ```

## Best Practices

1. Use Singularity containers for reproducibility
2. Set appropriate resource limits
3. Use array jobs for multiple files
4. Monitor resource usage
5. Save outputs to shared storage
6. Use job dependencies for workflows
