#!/usr/bin/env python3
import os
import sys
import subprocess
from typing import List

# Check if we are in a virtual environment
venv = os.environ.get("VIRTUAL_ENV")

if not venv:
    print("Not in a virtual environment. Creating one...")
    # Create a virtual environment
    try:
        upgrade_pip_cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
        ]
        subprocess.check_call(upgrade_pip_cmd)
        subprocess.check_call(
            [sys.executable, "-m", "pip", "-r", "requirements.txt"]
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        sys.exit(1)

    # Re-execute pre-commit in the virtual environment
    print("Re-executing pre-commit in the virtual environment...")
    execv_cmd = [sys.executable, __file__] + sys.argv[1:]
    os.execv(sys.executable, execv_cmd)


# Check for required tools in the local venv, before falling back to system
# checks
def check_tool_in_venv(tool: str) -> bool:
    venv_path = os.environ.get("VIRTUAL_ENV")
    if not venv_path or not os.path.isdir(venv_path):
        return False
    tool_path = os.path.join(venv_path, "bin", tool)
    return os.path.exists(tool_path)


def check_tool_exists(tool: str) -> bool:
    """Check if a tool exists in the system."""  # tool: redefined
    if check_tool_in_venv(tool):
        return True
    try:
        subprocess.check_call(
            ["which", tool],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


required_tools = ["black", "pylint"]

missing_tools: List[str] = []
for req_tool in required_tools:
    if not check_tool_exists(req_tool):
        missing_tools.append(req_tool)

if missing_tools:
    print(
        "Missing required tools:", ", ".join(missing_tools)
    )  # join: redefined
    print("Please install them using pip or your system package manager.")
    sys.exit(1)

print("Running black...")
try:
    subprocess.check_call(["black", "--line-length", "80", "."])
except subprocess.CalledProcessError as e:
    print(f"Black failed: {e}")
    sys.exit(1)

print("Running pylint...")
try:
    subprocess.check_call(["pylint"] + sys.argv[1:])
except subprocess.CalledProcessError as e:
    print(f"Pylint failed: {e}")
    sys.exit(1)

print("All checks passed!")
sys.exit(0)
