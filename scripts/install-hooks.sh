#!/bin/bash
# Install git hooks

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create .git/hooks if it doesn't exist
mkdir -p "${SCRIPT_DIR}/../.git/hooks"

# Create the pre-commit hook
PRE_COMMIT="${SCRIPT_DIR}/../.git/hooks/pre-commit"
echo '#!/bin/bash' > "$PRE_COMMIT"
echo 'exec python3 "$(git rev-parse --show-toplevel)/scripts/pre-commit.py"' >> "$PRE_COMMIT"
chmod +x "$PRE_COMMIT"

echo "Git hooks installed successfully!"
