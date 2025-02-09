#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil

if not os.getenv("VIRTUAL_ENV"):
    venv_path = os.path.join(os.getcwd(), "venv")
    if not os.path.exists(venv_path):
        print("Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
    print("Installing development dependencies in virtual environment...")
    subprocess.check_call(
        [
            os.path.join(venv_path, "bin", "pip"),
            "install",
            "-r",
            "requirements-dev.txt",
        ]
    )
    print("Re-executing pre-commit hook with virtual environment's python...")
    os.execv(
        os.path.join(venv_path, "bin", "python"),
        [os.path.join(venv_path, "bin", "python")] + sys.argv,
    )

"""Git pre-commit hook for WARC processor.

This script runs before each commit and:
1. Checks code formatting using yapf (Google style, 80 chars)
2. Runs pylint for style checking
3. Runs tests if Python files are modified

Only checks files that are being committed.
"""

import os
import subprocess
import sys
from typing import List, Tuple


def run_command(cmd: List[str], cwd: str = None) -> Tuple[int, str, str]:
    """Run a command and return its exit code and output.

    Args:
        cmd: Command to run as list of strings
        cwd: Working directory for command

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            cmd, cwd=cwd, check=False, capture_output=True, text=True
        )
        return result.returncode, result.stdout, result.stderr
    except (subprocess.SubprocessError, OSError) as e:
        return 1, "", str(e)


def check_dependencies() -> bool:
    """Check if required tools are installed. Returns True if all dependencies are present, False otherwise."""
    required_tools = ["yapf", "pylint", "pytest"]
    for tool in required_tools:
        if not shutil.which(tool):
            print(f"Error: {tool} not found. Please install it with pip.")
            return False
    return True


def get_staged_python_files() -> List[str]:
    """Get list of Python files staged for commit.

    Returns:
        List of staged Python file paths
    """
    code, out, _ = run_command(["git", "diff", "--cached", "--name-only"])
    if code != 0:
        return []

    return [
        f for f in out.splitlines() if f.endswith(".py") and os.path.exists(f)
    ]


def check_formatting(files: List[str]) -> bool:
    """Check if files are formatted according to Google style.

    Args:
        files: List of files to check

    Returns:
        True if all files are properly formatted, False otherwise
    """
    if not files:
        return True

    print("\nChecking code formatting...")
    yapf_style = "{based_on_style: google, column_limit: 80}"
    code, out, _ = run_command(
        ["yapf", "--style", yapf_style, "--diff"] + files
    )

    if code == 0 and not out:
        print("✓ All files are properly formatted")
        return True

    print("× Some files need formatting. Run:")
    print(f"yapf --style='{yapf_style}' -i <file>")
    if out:
        print("\nDiff:")
        print(out)
    return False


def run_pylint(files: List[str]) -> bool:
    """Run pylint on files.

    Args:
        files: List of files to check

    Returns:
        True if pylint passes, False otherwise
    """
    if not files:
        return True

    print("\nRunning pylint...")
    code, out, _ = run_command(["pylint"] + files)

    if code == 0:
        print("✓ Pylint checks passed")
        return True

    print("× Pylint found issues:")
    print(out)
    return False


def run_tests() -> bool:
    """Run pytest suite.

    Returns:
        True if all tests pass, False otherwise
    """
    print("\nRunning tests...")
    code, out, _ = run_command(["pytest", "tests/", "-v"])

    if code == 0:
        print("✓ All tests passed")
        return True

    print("× Some tests failed:")
    print(out)
    return False


def main() -> int:
    """Run pre-commit checks.

    Returns:
        0 if all checks pass, 1 otherwise
    """
    if not check_dependencies():
        return 1

    # Get Python files staged for commit
    python_files = get_staged_python_files()
    if not python_files:
        print("No Python files to check")
        return 0

    print(f"Checking {len(python_files)} Python files:")
    for f in python_files:
        print(f"  {f}")

    # Run checks
    format_ok = check_formatting(python_files)
    lint_ok = run_pylint(python_files)

    # Only run tests if there are Python changes
    tests_ok = run_tests()

    if format_ok and lint_ok and tests_ok:
        print("\n✓ All checks passed!")
        return 0

    print("\n× Some checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())

# trivial commit test
