#!/bin/bash

# Script to setup a test environment for JFMO development

# Colors for better visualization
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}JFMO Development Test Environment Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Create test directories
TEST_DIR="./test_environment"
DOWNLOADS_DIR="$TEST_DIR/downloads"
FILMS_DIR="$TEST_DIR/films"
SERIES_DIR="$TEST_DIR/series"

echo -e "${BLUE}Creating test directories...${NC}"
mkdir -p "$DOWNLOADS_DIR"
mkdir -p "$FILMS_DIR"
mkdir -p "$SERIES_DIR"

# Create test configuration
CONFIG_DIR="$TEST_DIR/config"
mkdir -p "$CONFIG_DIR"

CONFIG_FILE="$CONFIG_DIR/jfmo_test_config.json"

echo -e "${BLUE}Creating test configuration...${NC}"
cat > "$CONFIG_FILE" << EOL
{
    "directories": {
        "media_dir": "$(pwd)/$TEST_DIR",
        "downloads": "$(pwd)/$DOWNLOADS_DIR",
        "films": "$(pwd)/$FILMS_DIR",
        "series": "$(pwd)/$SERIES_DIR"
    },
    "permissions": {
        "user": "$(whoami)",
        "group": "$(id -gn)"
    },
    "tmdb": {
        "api_key": "",
        "enabled": true
    },
    "logging": {
        "log_file": "$(pwd)/$TEST_DIR/jfmo.log",
        "verbose": true
    }
}
EOL

# Create sample movie files
echo -e "${BLUE}Creating sample movie files...${NC}"
touch "$DOWNLOADS_DIR/The.Matrix.1999.1080p.mkv"
touch "$DOWNLOADS_DIR/Inception.2010.2160p.mkv"
touch "$DOWNLOADS_DIR/Interstellar.2014.720p.mp4"
touch "$DOWNLOADS_DIR/Oppenheimer.2023.HDR.2160p.mkv"
touch "$DOWNLOADS_DIR/Dune.Part.2.2024.1080p.mkv"

# Create sample TV show files
echo -e "${BLUE}Creating sample TV show files...${NC}"
touch "$DOWNLOADS_DIR/Severance.S01E01.1080p.mkv"
touch "$DOWNLOADS_DIR/Severance.S01E02.1080p.mkv"
touch "$DOWNLOADS_DIR/Stranger.Things.S04E01.2160p.mkv"
touch "$DOWNLOADS_DIR/House.of.the.Dragon.S01E01.1080p.mkv"

# Create a sample folder with TV episodes
SAMPLE_SERIES_DIR="$DOWNLOADS_DIR/The.Last.of.Us.S01.1080p"
mkdir -p "$SAMPLE_SERIES_DIR"
touch "$SAMPLE_SERIES_DIR/The.Last.of.Us.S01E01.1080p.mkv"
touch "$SAMPLE_SERIES_DIR/The.Last.of.Us.S01E02.1080p.mkv"
touch "$SAMPLE_SERIES_DIR/The.Last.of.Us.S01E03.1080p.mkv"

# Create a sample Russian TV show
RUSSIAN_SERIES_DIR="$DOWNLOADS_DIR/Podslushano.v.Rybinske.S01.2024.2160p"
mkdir -p "$RUSSIAN_SERIES_DIR"
touch "$RUSSIAN_SERIES_DIR/Podslushano.v.Rybinske.S01E01.2160p.mkv"
touch "$RUSSIAN_SERIES_DIR/Podslushano.v.Rybinske.S01E02.2160p.mkv"

# Create a sample La Casa de Papel folder
CASA_DIR="$DOWNLOADS_DIR/La Casa de Papel 3 - LostFilm.TV [1080p]"
mkdir -p "$CASA_DIR"
touch "$CASA_DIR/La.Casa.de.Papel.S03E01.1080p.mkv"
touch "$CASA_DIR/La.Casa.de.Papel.S03E02.1080p.mkv"

# Create a README for the test environment
README_FILE="$TEST_DIR/README.md"
cat > "$README_FILE" << EOL
# JFMO Test Environment

This directory contains a test environment for JFMO development.

## Structure

- \`downloads/\` - Sample media files to be processed
- \`films/\` - Target directory for movies
- \`series/\` - Target directory for TV shows
- \`config/\` - Test configuration

## Usage

To test JFMO with this environment:

\`\`\`bash
# Run in test mode (no actual changes)
python -m jfmo --config $(pwd)/$CONFIG_FILE --test

# Run with actual changes
python -m jfmo --config $(pwd)/$CONFIG_FILE
\`\`\`

No need for sudo since the configuration uses your current user.

## Sample Files

This environment includes sample files for:

- Movies (various years and qualities)
- TV Shows (individual files and directories)
- Special case: La Casa de Papel
- Russian TV Show for transliteration testing
EOL

echo ""
echo -e "${GREEN}✅ Test environment created successfully!${NC}"
echo ""
echo -e "${YELLOW}To test JFMO, run:${NC}"
echo -e "${BLUE}python -m jfmo --config $CONFIG_FILE --test${NC}"
echo ""
echo -e "${YELLOW}To run with actual changes:${NC}"
echo -e "${BLUE}python -m jfmo --config $CONFIG_FILE${NC}"
echo ""
echo -e "${YELLOW}Test environment located at:${NC} $(pwd)/$TEST_DIR"
echo ""