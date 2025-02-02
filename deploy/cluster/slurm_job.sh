#!/bin/bash
#SBATCH --job-name=warc-process
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=01:00:00
#SBATCH --output=warc-process-%j.out
#SBATCH --error=warc-process-%j.err

# Load Singularity module if needed
# module load singularity

# Run the WARC processor inside the container
singularity run \
    --bind /path/to/input/data:/data \
    /path/to/warc-processor.sif \
    --input /data/input.warc \
    --output /data/output
