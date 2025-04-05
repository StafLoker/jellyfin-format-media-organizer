#!/bin/bash

# Script to setup a test environment for JFMO development
# Updated to use a single downloads directory for all files

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
    },
    "options": {
        "interactive": true
    }
}
EOL

echo -e "${BLUE}Creating sample files in downloads directory...${NC}"

# ----- VALID MOVIE PATTERNS -----
# Standard movie pattern (Title + Year + Quality)
touch "$DOWNLOADS_DIR/The.Matrix.1999.1080p.mkv"
touch "$DOWNLOADS_DIR/Inception.2010.2160p.mkv"
touch "$DOWNLOADS_DIR/Interstellar.2014.720p.mp4"
touch "$DOWNLOADS_DIR/Oppenheimer.2023.HDR.2160p.mkv"
touch "$DOWNLOADS_DIR/Dune.Part.2.2024.1080p.mkv"

# Movies with non-standard formatting but valid patterns
touch "$DOWNLOADS_DIR/The_Shawshank_Redemption_1994_720p.mkv"
touch "$DOWNLOADS_DIR/Pulp-Fiction-1994-1080p.mkv"
touch "$DOWNLOADS_DIR/Avatar (2009) 2160p WEB-DL.mkv"

# ----- VALID TV SHOW PATTERNS -----
# Standard SxxExx pattern
touch "$DOWNLOADS_DIR/Severance.S01E01.1080p.mkv"
touch "$DOWNLOADS_DIR/Severance.S01E02.1080p.mkv"
touch "$DOWNLOADS_DIR/Stranger.Things.S04E01.2160p.mkv"
touch "$DOWNLOADS_DIR/House.of.the.Dragon.S01E01.1080p.mkv"

# S01.E01 pattern
touch "$DOWNLOADS_DIR/Breaking.Bad.S01.E01.720p.mkv"
touch "$DOWNLOADS_DIR/Better.Call.Saul.S03.E05.1080p.mkv"

# La Casa de Papel episodes
touch "$DOWNLOADS_DIR/La.Casa.de.Papel.S03E01.1080p.mkv"
touch "$DOWNLOADS_DIR/La.Casa.de.Papel.S03E02.1080p.mkv"

# ----- PROBLEMATIC PATTERNS -----
# Season x Episode format (3x07)
touch "$DOWNLOADS_DIR/Game.of.Thrones.3x07.1080p.mkv"
touch "$DOWNLOADS_DIR/Friends.5x12.720p.mkv"

# Episode number only
touch "$DOWNLOADS_DIR/The.Mandalorian.Episode.5.1080p.mkv"
touch "$DOWNLOADS_DIR/Loki.Episode.3.2160p.mkv"

# Season number followed by episode number without SxxExx
touch "$DOWNLOADS_DIR/Breaking.Bad.401.720p.mkv"
touch "$DOWNLOADS_DIR/Game.of.Thrones.801.1080p.mkv"

# Date-based episodes
touch "$DOWNLOADS_DIR/The.Daily.Show.2023.06.15.720p.mkv"
touch "$DOWNLOADS_DIR/Late.Night.2024-03-22.1080p.mkv"

# Special episodes
touch "$DOWNLOADS_DIR/Doctor.Who.Christmas.Special.2023.1080p.mkv"
touch "$DOWNLOADS_DIR/Stranger.Things.Bonus.Content.720p.mkv"

# Movies with numbers that could be confused with episodes
touch "$DOWNLOADS_DIR/Ocean's.11.2001.1080p.mkv"
touch "$DOWNLOADS_DIR/2001.A.Space.Odyssey.1968.2160p.mkv"

# Series with years as titles that could be confused
touch "$DOWNLOADS_DIR/1883.S01E01.1080p.mkv"
touch "$DOWNLOADS_DIR/1923.S01E02.720p.mkv"

# Russian transliteration examples
touch "$DOWNLOADS_DIR/Podslushano.v.Rybinske.S01E01.2160p.mkv"
touch "$DOWNLOADS_DIR/Podslushano.v.Rybinske.S01E02.2160p.mkv"

# Another Russian series with different naming pattern
touch "$DOWNLOADS_DIR/Kvartirnyj.Vopros.vypusk.ot.2024.03.16.720p.mkv"
touch "$DOWNLOADS_DIR/Tainstvennye.Istorii.e05.2023.1080p.mkv"

# Edge cases with mixed patterns
touch "$DOWNLOADS_DIR/The.100.S01E01.1080p.mkv"  # "The 100" might be interpreted as movie from year 100
touch "$DOWNLOADS_DIR/9-1-1.S02E03.720p.mkv"     # Hyphenated name with numbers
touch "$DOWNLOADS_DIR/24.S01E01.1080p.mkv"       # Single number title

# Multi-episode files
touch "$DOWNLOADS_DIR/Westworld.S01E01-E02.1080p.mkv"
touch "$DOWNLOADS_DIR/Succession.S03E01-02.720p.mkv"
touch "$DOWNLOADS_DIR/The.Last.of.Us.S01E01.E02.2160p.mkv"

# Create a README for the test environment
README_FILE="$TEST_DIR/README.md"
cat > "$README_FILE" << EOL
# JFMO Test Environment

This directory contains a comprehensive test environment for JFMO development with various file patterns.

## File Pattern Categories

### Valid Patterns (should be detected correctly)
- Standard movie patterns (Title.Year.Quality)
- Standard TV show patterns (SxxExx)
- Alternative formats that should work (S01.E01)
- Special case: La Casa de Papel

### Problematic Patterns (challenging for detection)
- Season x Episode format (3x07)
- Episode numbers without season (Episode 5)
- Combined numbers (801 for S08E01)
- Date-based episodes (2023.06.15)
- Special episodes
- Movies with numbers in titles
- Series with years as titles
- Russian transliteration examples
- Edge cases with mixed patterns
- Multi-episode files

## Usage

To test JFMO with this environment:

\`\`\`bash
# Run in test mode (no actual changes)
python3 -m jfmo --config $(pwd)/$CONFIG_FILE --test

# Run with interactive mode (recommended for testing problematic patterns)
python3 -m jfmo --config $(pwd)/$CONFIG_FILE

# Run without interactive mode
python3 -m jfmo --config $(pwd)/$CONFIG_FILE --non-interactive
\`\`\`

## Expected Behavior

1. Movie files should be detected and moved to the films directory
2. TV show files should be detected and organized in the series directory
3. Some problematic patterns may face issues:
   - Some may be incorrectly categorized (movies as TV or vice versa)
   - Some may be skipped with error messages
   - Some might work correctly despite the complex patterns

This allows testing both the detection capabilities and the error handling of JFMO.
EOL

# Create a helpful info file in the downloads directory
INFO_FILE="$DOWNLOADS_DIR/README.txt"
cat > "$INFO_FILE" << EOL
This directory contains various media files with different naming patterns to test JFMO.
The files are deliberately mixed (movies and TV shows) to simulate a real-world downloads folder.
EOL

echo ""
echo -e "${GREEN}✅ Realistic test environment created successfully!${NC}"
echo ""
echo -e "${YELLOW}To test JFMO, run:${NC}"
echo -e "${BLUE}python3 -m jfmo --config $CONFIG_FILE --test${NC}"
echo ""
echo -e "${YELLOW}For interactive testing:${NC}"
echo -e "${BLUE}python3 -m jfmo --config $CONFIG_FILE${NC}"
echo ""
echo -e "${YELLOW}Test environment located at:${NC} $(pwd)/$TEST_DIR"
echo -e "${YELLOW}See $(pwd)/$TEST_DIR/README.md for details on test patterns${NC}"
echo ""