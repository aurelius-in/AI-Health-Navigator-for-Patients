#!/bin/bash

echo "Starting AI Health Navigator Demo..."
echo ""
echo "Opening demo in your default browser..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEMO_FILE="$SCRIPT_DIR/launch-demo.html"

# Try to open the demo HTML file with the default browser
if command -v xdg-open >/dev/null 2>&1; then
    # Linux
    xdg-open "$DEMO_FILE"
elif command -v open >/dev/null 2>&1; then
    # macOS
    open "$DEMO_FILE"
elif command -v start >/dev/null 2>&1; then
    # Windows (if running in WSL or similar)
    start "$DEMO_FILE"
else
    echo "Could not automatically open browser. Please manually open:"
    echo "$DEMO_FILE"
fi

echo "Demo launched successfully!"
echo ""
echo "If the demo doesn't open automatically, please:"
echo "1. Navigate to the demo folder"
echo "2. Open launch-demo.html in your web browser"
echo ""
echo "Demo file location: $DEMO_FILE"
