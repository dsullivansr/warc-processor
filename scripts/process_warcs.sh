#!/bin/bash
# Main script for parallel WARC file processing

# Source the library
source "$(dirname "$0")/warc_batch_processing.sh"

# Default values
max_jobs=$(nproc)  # Number of CPU cores
input_dir=""
output_dir=""
verbose=0
start_time=$(date +%s)

usage() {
    cat << EOF
Usage: $(basename "$0") -i INPUT_DIR -o OUTPUT_DIR [-j JOBS] [-v]

Process multiple WARC files in parallel using warc-processor.

Required arguments:
    -i INPUT_DIR   Directory containing WARC files
    -o OUTPUT_DIR  Directory for output files (will be created if it doesn't exist)

Optional arguments:
    -j JOBS        Maximum number of parallel jobs (default: number of CPU cores)
    -v             Enable verbose output
    -h             Show this help message

Example:
    $(basename "$0") -i /path/to/warcs -o /path/to/output -j 4
EOF
}

# Parse command line arguments
while getopts "i:o:j:vh" opt; do
    case $opt in
        i) input_dir="$OPTARG";;
        o) output_dir="$OPTARG";;
        j) max_jobs="$OPTARG";;
        v) verbose=1;;
        h) usage; exit 0;;
        *) usage; exit 1;;
    esac
done

# Check dependencies before proceeding
if ! check_dependencies; then
    exit 1
fi

# Validate required arguments
if [[ -z "$input_dir" || -z "$output_dir" ]]; then
    echo -e "${RED}Error: Input and output directories are required${NC}" >&2
    usage
    exit 1
fi

# Validate input directory exists
if [[ ! -d "$input_dir" ]]; then
    echo -e "${RED}Error: Input directory does not exist: $input_dir${NC}" >&2
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$output_dir"

# Export functions needed by parallel
export -f process_warc format_size get_file_size

# Create a named pipe for progress updates
progress_pipe="/tmp/warc_progress_$$"
mkfifo "$progress_pipe"
exec 3>"$progress_pipe"

# Start progress monitor in background
{
    success_count=0
    error_count=0
    total_files=0
    total_size=0
    processed_size=0
    
    # Count total files and size
    while IFS= read -r -d '' file; do
        ((total_files++))
        size=$(get_file_size "$file")
        ((total_size += size))
    done < <(find "$input_dir" -type f \( -name "*.warc" -o -name "*.warc.gz" \) -print0)
    
    echo -e "${GREEN}Starting processing of $total_files WARC files"\
        "($(format_size "$total_size"))...${NC}"
    
    # Process progress updates
    while read -r status file size; do
        case "$status" in
            "SUCCESS") 
                ((success_count++))
                ((processed_size += size))
                ;;
            "ERROR") 
                ((error_count++))
                ((processed_size += size))
                ;;
        esac
        
        processed=$((success_count + error_count))
        percent=$((processed * 100 / total_files))
        elapsed=$(($(date +%s) - start_time))
        eta=$(calculate_eta "$processed_size" "$total_size" "$elapsed")
        
        if [ "$processed" -gt 0 ] && [ "$elapsed" -gt 0 ]; then
            rate=$((processed_size / elapsed))
        else
            rate=0
        fi
        
        printf "\rProgress: %d%% (%d/%d) - %s/%s - Success: %d, Errors: %d - "\
            "$percent" "$processed" "$total_files" \
            "$(format_size "$processed_size")" "$(format_size "$total_size")" \
            "$success_count" "$error_count"
        
        printf "Rate: %s/s - ETA: %s" \
            "$(format_size "$rate")" "$(format_time "$eta")"
            
    done < "$progress_pipe"
    
    elapsed=$(($(date +%s) - start_time))
    avg_rate=$((total_size / (elapsed + 1)))  # +1 to avoid division by zero
    
    echo
    echo -e "${GREEN}Processing complete in $(format_time "$elapsed"):${NC}"
    echo "  Successfully processed: $success_count files"
    echo "  Errors encountered: $error_count files"
    echo "  Total processed: $total_files files ($(format_size "$total_size"))"
    echo "  Average rate: $(format_size "$avg_rate")/s"
    
    # Clean up
    rm "$progress_pipe"
} &

# Process all WARC files in parallel
find "$input_dir" -type f \( -name "*.warc" -o -name "*.warc.gz" \) -print0 | \
    parallel -0 -j "$max_jobs" \
        process_warc {} "$output_dir/{/.}.txt" "$verbose" "$input_dir" 3

# Wait for progress monitor to finish
wait

# Exit with error if any files failed
if [[ $error_count -gt 0 ]]; then
    exit 1
fi
