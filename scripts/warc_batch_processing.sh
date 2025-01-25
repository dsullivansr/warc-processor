#!/bin/bash
# Library of functions for WARC batch processing

# Exit on error, undefined variables, and pipe failures
set -euo pipefail

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

format_time() {
    # Convert seconds to HH:MM:SS format
    # Args:
    #   $1: time in seconds
    # Returns:
    #   Formatted time string
    local seconds=$1
    local hours=$((seconds / 3600))
    local minutes=$(((seconds % 3600) / 60))
    local secs=$((seconds % 60))
    printf "%02d:%02d:%02d" "$hours" "$minutes" "$secs"
}

format_size() {
    # Format byte size to human readable format
    # Args:
    #   $1: size in bytes
    # Returns:
    #   Formatted size string with units
    local size=$1
    if [ "$size" -ge 1073741824 ]; then
        printf "%.1f GB" "$(echo "scale=1; $size / 1073741824" | bc)"
    elif [ "$size" -ge 1048576 ]; then
        printf "%.1f MB" "$(echo "scale=1; $size / 1048576" | bc)"
    elif [ "$size" -ge 1024 ]; then
        printf "%.1f KB" "$(echo "scale=1; $size / 1024" | bc)"
    else
        printf "%d B" "$size"
    fi
}

get_file_size() {
    # Get file size in bytes, works on both BSD and GNU systems
    # Args:
    #   $1: file path
    # Returns:
    #   File size in bytes
    local file=$1
    stat -f %z "$file" 2>/dev/null || stat -c %s "$file"
}

check_command() {
    # Check if a command exists
    # Args:
    #   $1: command name
    # Returns:
    #   0 if exists, 1 if not
    command -v "$1" >/dev/null 2>&1
}

check_gnu_parallel() {
    # Check if GNU Parallel is installed and properly configured
    # Returns:
    #   0 if GNU Parallel is available, 1 if not
    if ! check_command parallel; then
        return 1
    fi
    parallel --version 2>/dev/null | grep -q "GNU parallel"
}

check_dependencies() {
    # Check all required dependencies
    # Returns:
    #   0 if all dependencies are met, 1 if not
    local missing_deps=()
    
    if ! check_gnu_parallel; then
        missing_deps+=("parallel")
    fi
    
    if ! check_command python3; then
        missing_deps+=("python3")
    fi
    
    if ! python3 -c "import warc_processor" 2>/dev/null; then
        echo -e "${YELLOW}Warning: warc-processor module not found in Python path${NC}" >&2
        echo "Make sure you're running this script from the warc-processor directory" >&2
        echo "or the package is installed in your Python environment" >&2
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo -e "${RED}Error: Missing required dependencies:${NC} ${missing_deps[*]}" >&2
        echo "Please install them using your package manager:" >&2
        echo "  apt install ${missing_deps[*]}  # For Debian/Ubuntu" >&2
        echo "  yum install ${missing_deps[*]}  # For RHEL/CentOS" >&2
        return 1
    fi
    
    return 0
}

process_warc() {
    # Process a single WARC file
    # Args:
    #   $1: input WARC file path
    #   $2: output file path
    #   $3: verbose flag (0 or 1)
    #   $4: input directory (for relative path calculation)
    #   $5: file descriptor for progress pipe
    local warc_file=$1
    local output_file=$2
    local verbose=$3
    local input_dir=$4
    local progress_fd=$5
    local file_size
    file_size=$(get_file_size "$warc_file")
    
    # Get relative path for display
    local rel_path
    rel_path="${warc_file#$input_dir/}"
    
    if [[ $verbose -eq 1 ]]; then
        echo -e "${GREEN}Processing:${NC} $rel_path ($(format_size "$file_size"))"
    fi
    
    # Create output directory structure if needed
    mkdir -p "$(dirname "$output_file")"
    
    # Process the WARC file
    if python3 "$warc_file" "$output_file"; then
        if [[ $verbose -eq 1 ]]; then
            echo -e "${GREEN}Completed:${NC} $rel_path"
        fi
        echo "SUCCESS $rel_path $file_size" >&"$progress_fd"
        return 0
    else
        echo -e "${RED}Failed:${NC} $rel_path" >&2
        echo "ERROR $rel_path $file_size" >&"$progress_fd"
        return 1
    fi
}

calculate_eta() {
    # Calculate estimated time remaining
    # Args:
    #   $1: processed size in bytes
    #   $2: total size in bytes
    #   $3: elapsed time in seconds
    # Returns:
    #   Estimated time remaining in seconds
    local processed_size=$1
    local total_size=$2
    local elapsed=$3
    
    if [ "$processed_size" -gt 0 ] && [ "$elapsed" -gt 0 ]; then
        local rate=$((processed_size / elapsed))
        echo $(( (total_size - processed_size) / rate ))
    else
        echo 0
    fi
}
