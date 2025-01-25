#!/bin/bash
# Unit tests for WARC batch processing functions

# Source the library
source "$(dirname "$0")/../warc_batch_processing.sh"

# Test counter
tests_run=0
tests_passed=0
tests_failed=0

# Test utilities
assert_equals() {
    local expected=$1
    local actual=$2
    local message=$3
    ((tests_run++))
    
    if [ "$expected" = "$actual" ]; then
        echo -e "${GREEN}PASS${NC}: $message"
        ((tests_passed++))
        return 0
    else
        echo -e "${RED}FAIL${NC}: $message"
        echo "  Expected: $expected"
        echo "  Got: $actual"
        ((tests_failed++))
        return 1
    fi
}

# Test format_time
test_format_time() {
    echo "Testing format_time..."
    local result
    
    result=$(format_time 3661)  # 1h 1m 1s
    assert_equals "01:01:01" "$result" "format_time handles hours, minutes, seconds"
    
    result=$(format_time 0)
    assert_equals "00:00:00" "$result" "format_time handles zero"
    
    result=$(format_time 86399)  # 23h 59m 59s
    assert_equals "23:59:59" "$result" "format_time handles max daily time"
}

# Test format_size
test_format_size() {
    echo "Testing format_size..."
    local result
    
    result=$(format_size 1024)
    assert_equals "1.0 KB" "$result" "format_size handles kilobytes"
    
    result=$(format_size 1048576)
    assert_equals "1.0 MB" "$result" "format_size handles megabytes"
    
    result=$(format_size 1073741824)
    assert_equals "1.0 GB" "$result" "format_size handles gigabytes"
    
    result=$(format_size 500)
    assert_equals "500 B" "$result" "format_size handles bytes"
}

# Test check_command
test_check_command() {
    echo "Testing check_command..."
    local result
    
    check_command "ls"
    result=$?
    assert_equals 0 "$result" "check_command finds existing command"
    
    check_command "nonexistentcommand123"
    result=$?
    assert_equals 1 "$result" "check_command handles nonexistent command"
}

# Test calculate_eta
test_calculate_eta() {
    echo "Testing calculate_eta..."
    local result
    
    # Test with 50% complete, 1GB total, 60 seconds elapsed
    result=$(calculate_eta 536870912 1073741824 60)
    assert_equals "60" "$result" "calculate_eta estimates remaining time correctly"
    
    # Test with no progress
    result=$(calculate_eta 0 1073741824 60)
    assert_equals "0" "$result" "calculate_eta handles no progress"
}

# Mock functions for process_warc test
mkdir() {
    return 0
}

python3() {
    local input_file=$1
    local output_file=$2
    if [[ "$input_file" == *"success.warc" ]]; then
        echo "Processed content" >&3
        return 0
    else
        return 1
    fi
}

get_file_size() {
    echo "1024"
}

# Test process_warc
test_process_warc() {
    echo "Testing process_warc..."
    
    # Create a temporary file for progress output
    local progress_output
    progress_output=$(mktemp)
    
    # Mock functions
    export -f mkdir
    export -f python3
    export -f get_file_size
    
    # First test: successful processing
    exec 3>"$progress_output"
    process_warc "/input/success.warc" "/output/success.txt" 0 "/input" 3
    local result=$?
    assert_equals 0 "$result" "process_warc returns success"
    
    # Check if progress was written
    if grep -q "SUCCESS.*success.warc" "$progress_output"; then
        assert_equals "0" "0" "process_warc writes success progress"
    else
        assert_equals "0" "1" "process_warc writes success progress"
    fi
    
    # Second test: failed processing
    process_warc "/input/fail.warc" "/output/fail.txt" 0 "/input" 3
    result=$?
    assert_equals 1 "$result" "process_warc returns failure on error"
    
    if grep -q "ERROR.*fail.warc" "$progress_output"; then
        assert_equals "0" "0" "process_warc writes error progress"
    else
        assert_equals "0" "1" "process_warc writes error progress"
    fi
    
    # Clean up
    exec 3>&-
    rm -f "$progress_output"
    
    # Unset mock functions
    unset -f mkdir
    unset -f python3
    unset -f get_file_size
}

# Run all tests
run_tests() {
    echo "Running unit tests..."
    test_format_time || echo "format_time tests failed"
    test_format_size || echo "format_size tests failed"
    test_check_command || echo "check_command tests failed"
    test_calculate_eta || echo "calculate_eta tests failed"
    test_process_warc || echo "process_warc tests failed"
    
    echo
    echo "Test Summary:"
    echo "  Total tests: $tests_run"
    echo "  Passed: $tests_passed"
    echo "  Failed: $tests_failed"
    
    if [ "$tests_failed" -eq 0 ]; then
        echo -e "${GREEN}All tests passed!${NC}"
        return 0
    else
        echo -e "${RED}Some tests failed${NC}"
        return 1
    fi
}

# Run tests if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_tests
fi
