# Might find API keys

#!/bin/bash

# File to store results
RESULT_FILE="api_keys.txt"
> "$RESULT_FILE"  # Clear previous results

# Patterns to look for
PATTERNS=(
    "[A-Za-z0-9_-]{32,}"           # Generic long token (32+ chars)
    "[A-Za-z0-9+/]{40,}={0,2}"     # Base64-looking strings
    "(?i)API"                       # Case-insensitive "API"
)

# Get the script filename to exclude
SCRIPT_NAME=$(basename "$0")

echo "🔍 Scanning all files (including hidden), excluding $SCRIPT_NAME and $RESULT_FILE ..."

# Recursively find files, excluding the script itself AND the output file
find . -type f ! -name "$SCRIPT_NAME" ! -name "$RESULT_FILE" -print0 | while IFS= read -r -d '' file; do
    for pattern in "${PATTERNS[@]}"; do
        # Use grep with Perl regex for advanced patterns
        matches=$(grep -P -H -o "$pattern" "$file" 2>/dev/null)
        if [ -n "$matches" ]; then
            echo "File: $file" >> "$RESULT_FILE"
            echo "$matches" >> "$RESULT_FILE"
            echo "------------------------" >> "$RESULT_FILE"
        fi
    done
done

echo "✅ Scan complete! Results saved to $RESULT_FILE"
