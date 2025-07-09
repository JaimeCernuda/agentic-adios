#!/bin/bash

# Export Gemini CLI Telemetry Data - Manual Export Script
# This script creates timestamped archives of telemetry data for backup and analysis

set -e

# Configuration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
EXPORT_DIR="./telemetry-exports"
ARCHIVE_NAME="gemini-cli-telemetry-${TIMESTAMP}.tar.gz"
TELEMETRY_DATA_DIR="./telemetry-data"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Gemini CLI Telemetry Export Script${NC}"
echo -e "${BLUE}=====================================${NC}"
echo

# Check if telemetry data exists
if [ ! -d "$TELEMETRY_DATA_DIR" ]; then
    echo -e "${RED}❌ Error: Telemetry data directory not found: $TELEMETRY_DATA_DIR${NC}"
    exit 1
fi

# Check if telemetry data has content
if [ -z "$(ls -A $TELEMETRY_DATA_DIR)" ]; then
    echo -e "${YELLOW}⚠️  Warning: Telemetry data directory is empty${NC}"
    echo -e "${YELLOW}   Make sure to run Gemini CLI with telemetry enabled first${NC}"
    exit 1
fi

# Create export directory
mkdir -p "$EXPORT_DIR"

echo -e "${BLUE}📊 Analyzing telemetry data...${NC}"

# Show data summary
echo -e "${YELLOW}Data Summary:${NC}"
echo "  Directory: $TELEMETRY_DATA_DIR"
echo "  Files found:"
for file in "$TELEMETRY_DATA_DIR"/*; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        size=$(du -h "$file" | cut -f1)
        lines=$(wc -l < "$file" 2>/dev/null || echo "0")
        echo "    📄 $filename (${size}, ${lines} lines)"
    fi
done
echo

# Generate analysis report
echo -e "${BLUE}📋 Generating analysis report...${NC}"
if command -v uv &> /dev/null; then
    if (cd ../telemetry_analyzer && uv run telemetry --data-path "../gemini_cli_telemetry/$TELEMETRY_DATA_DIR" --output "../gemini_cli_telemetry/$EXPORT_DIR/report-${TIMESTAMP}.md" --export "../gemini_cli_telemetry/$EXPORT_DIR/data-${TIMESTAMP}.json" --no-display); then
        echo -e "${GREEN}✅ Analysis report generated successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Analysis report generation failed, continuing with data export${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  'uv' not found, skipping analysis report generation${NC}"
fi

# Create archive
echo -e "${BLUE}📦 Creating archive...${NC}"
tar -czf "$EXPORT_DIR/$ARCHIVE_NAME" \
    -C "$(dirname "$TELEMETRY_DATA_DIR")" \
    "$(basename "$TELEMETRY_DATA_DIR")" \
    --exclude="*.tmp" \
    --exclude="*.lock"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Archive created successfully: $EXPORT_DIR/$ARCHIVE_NAME${NC}"
else
    echo -e "${RED}❌ Error creating archive${NC}"
    exit 1
fi

# Show archive details
archive_size=$(du -h "$EXPORT_DIR/$ARCHIVE_NAME" | cut -f1)
echo -e "${YELLOW}Archive Details:${NC}"
echo "  📁 File: $EXPORT_DIR/$ARCHIVE_NAME"
echo "  📏 Size: $archive_size"
echo "  🕐 Created: $(date)"
echo

# List contents of export directory
echo -e "${BLUE}📂 Export directory contents:${NC}"
ls -la "$EXPORT_DIR"
echo

# Cleanup old archives (keep last 10)
echo -e "${BLUE}🧹 Cleaning up old archives...${NC}"
cd "$EXPORT_DIR"
ls -t gemini-cli-telemetry-*.tar.gz 2>/dev/null | tail -n +11 | xargs -r rm -f
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Old archives cleaned up (kept last 10)${NC}"
fi

echo
echo -e "${GREEN}🎉 Export complete!${NC}"
echo -e "${GREEN}   📦 Archive: $EXPORT_DIR/$ARCHIVE_NAME${NC}"
echo -e "${GREEN}   📊 Report: $EXPORT_DIR/report-${TIMESTAMP}.md${NC}"
echo -e "${GREEN}   📄 Data: $EXPORT_DIR/data-${TIMESTAMP}.json${NC}"
echo

# Show usage instructions
echo -e "${BLUE}💡 Usage Instructions:${NC}"
echo "  To extract the archive:"
echo "    tar -xzf $EXPORT_DIR/$ARCHIVE_NAME"
echo
echo "  To analyze the data:"
echo "    uv run telemetry --data-path ./telemetry-data"
echo
echo "  To view the report:"
echo "    cat $EXPORT_DIR/report-${TIMESTAMP}.md"
echo