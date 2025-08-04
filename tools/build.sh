#!/bin/bash

# Eva Icons Flutter - Build Script
# This script orchestrates the complete generation process for Eva Icons Flutter

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}Eva Icons Flutter - Build Script${NC}"
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed${NC}"
    exit 1
fi

# Check if font file exists
FONT_PATH="$PROJECT_ROOT/lib/fonts/Eva-Icons.ttf"
if [ ! -f "$FONT_PATH" ]; then
    echo -e "${RED}Error: Font file not found at $FONT_PATH${NC}"
    exit 1
fi

echo -e "${YELLOW}Setting up Python environment...${NC}"

# Create virtual environment if it doesn't exist
VENV_PATH="$SCRIPT_DIR/venv"
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$VENV_PATH"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Install/upgrade required packages
echo "Installing Python dependencies..."
pip install --upgrade pip fonttools

echo -e "${YELLOW}Generating icon library...${NC}"

# Run the icon generation script
cd "$SCRIPT_DIR"
python generate_icons.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Icon generation completed successfully${NC}"
else
    echo -e "${RED}✗ Icon generation failed${NC}"
    exit 1
fi

# Format the generated Dart code
echo -e "${YELLOW}Formatting generated Dart code...${NC}"
cd "$PROJECT_ROOT"

if command -v dart &> /dev/null; then
    dart format lib/src/eva_icons_flutter.dart
    echo -e "${GREEN}✓ Dart code formatted${NC}"
else
    echo -e "${YELLOW}Warning: dart command not found, skipping code formatting${NC}"
fi

# Run analysis if available
if command -v flutter &> /dev/null; then
    echo -e "${YELLOW}Running Flutter analysis...${NC}"
    flutter analyze
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Analysis passed${NC}"
    else
        echo -e "${YELLOW}Warning: Analysis found issues${NC}"
    fi
else
    echo -e "${YELLOW}Warning: flutter command not found, skipping analysis${NC}"
fi

echo ""
echo -e "${GREEN}Build completed successfully!${NC}"
echo ""
echo "Generated files:"
echo "  - lib/src/eva_icons_flutter.dart (Updated icon constants)"
echo "  - tools/eva_icons_mappings.json (Metadata reference)"
echo ""
echo "Next steps:"
echo "  1. Review the generated code in lib/src/eva_icons_flutter.dart"
echo "  2. Test the icons in your Flutter app"
echo "  3. Commit the changes to version control"
echo ""

# Deactivate virtual environment
deactivate