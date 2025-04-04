#!/bin/bash

# Script to setup a test environment for JFMO development
# Updated with comprehensive test cases covering supported and problematic patterns

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

# Create a subdirectory for valid pattern examples
VALID_PATTERNS_DIR="$DOWNLOADS_DIR/valid_patterns"
mkdir -p "$VALID_PATTERNS_DIR"

echo -e "${BLUE}Creating sample valid pattern files...${NC}"

# ----- VALID MOVIE PATTERNS -----
# Standard movie pattern (Title + Year + Quality)
touch "$VALID_PATTERNS_DIR/The.Matrix.1999.1080p.mkv"
touch "$VALID_PATTERNS_DIR/Inception.2010.2160p.mkv"
touch "$VALID_PATTERNS_DIR/Interstellar.2014.720p.mp4"
touch "$VALID_PATTERNS_DIR/Oppenheimer.2023.HDR.2160p.mkv"
touch "$VALID_PATTERNS_DIR/Dune.Part.2.2024.1080p.mkv"

# Movies with non-standard formatting but valid patterns
touch "$VALID_PATTERNS_DIR/The_Shawshank_Redemption_1994_720p.mkv"
touch "$VALID_PATTERNS_DIR/Pulp-Fiction-1994-1080p.mkv"
touch "$VALID_PATTERNS_DIR/Avatar (2009) 2160p WEB-DL.mkv"

# ----- VALID TV SHOW PATTERNS -----
# Standard SxxExx pattern
touch "$VALID_PATTERNS_DIR/Severance.S01E01.1080p.mkv"
touch "$VALID_PATTERNS_DIR/Severance.S01E02.1080p.mkv"
touch "$VALID_PATTERNS_DIR/Stranger.Things.S04E01.2160p.mkv"
touch "$VALID_PATTERNS_DIR/House.of.the.Dragon.S01E01.1080p.mkv"

# S01.E01 pattern
touch "$VALID_PATTERNS_DIR/Breaking.Bad.S01.E01.720p.mkv"
touch "$VALID_PATTERNS_DIR/Better.Call.Saul.S03.E05.1080p.mkv"

# La Casa de Papel special case
CASA_DIR="$DOWNLOADS_DIR/La Casa de Papel 3 - LostFilm.TV [1080p]"
mkdir -p "$CASA_DIR"
touch "$CASA_DIR/La.Casa.de.Papel.S03E01.1080p.mkv"
touch "$CASA_DIR/La.Casa.de.Papel.S03E02.1080p.mkv"

# Create a subdirectory for problematic pattern examples
PROBLEM_PATTERNS_DIR="$DOWNLOADS_DIR/problematic_patterns"
mkdir -p "$PROBLEM_PATTERNS_DIR"

echo -e "${BLUE}Creating sample problematic pattern files...${NC}"

# ----- PROBLEMATIC PATTERNS -----
# Season x Episode format (3x07)
touch "$PROBLEM_PATTERNS_DIR/Game.of.Thrones.3x07.1080p.mkv"
touch "$PROBLEM_PATTERNS_DIR/Friends.5x12.720p.mkv"

# Episode number only
touch "$PROBLEM_PATTERNS_DIR/The.Mandalorian.Episode.5.1080p.mkv"
touch "$PROBLEM_PATTERNS_DIR/Loki.Episode.3.2160p.mkv"

# Season number followed by episode number without SxxExx
touch "$PROBLEM_PATTERNS_DIR/Breaking.Bad.401.720p.mkv"
touch "$PROBLEM_PATTERNS_DIR/Game.of.Thrones.801.1080p.mkv"

# Date-based episodes
touch "$PROBLEM_PATTERNS_DIR/The.Daily.Show.2023.06.15.720p.mkv"
touch "$PROBLEM_PATTERNS_DIR/Late.Night.2024-03-22.1080p.mkv"

# Special episodes
touch "$PROBLEM_PATTERNS_DIR/Doctor.Who.Christmas.Special.2023.1080p.mkv"
touch "$PROBLEM_PATTERNS_DIR/Stranger.Things.Bonus.Content.720p.mkv"

# Movies with numbers that could be confused with episodes
touch "$PROBLEM_PATTERNS_DIR/Ocean's.11.2001.1080p.mkv"
touch "$PROBLEM_PATTERNS_DIR/2001.A.Space.Odyssey.1968.2160p.mkv"

# Series with years as titles that could be confused
touch "$PROBLEM_PATTERNS_DIR/1883.S01E01.1080p.mkv"
touch "$PROBLEM_PATTERNS_DIR/1923.S01E02.720p.mkv"

# Russian transliteration examples
RUSSIAN_SERIES_DIR="$DOWNLOADS_DIR/Podslushano.v.Rybinske.S01.2024.2160p"
mkdir -p "$RUSSIAN_SERIES_DIR"
touch "$RUSSIAN_SERIES_DIR/Podslushano.v.Rybinske.S01E01.2160p.mkv"
touch "$RUSSIAN_SERIES_DIR/Podslushano.v.Rybinske.S01E02.2160p.mkv"

# Another Russian series with different naming pattern
touch "$PROBLEM_PATTERNS_DIR/Kvartirnyj.Vopros.vypusk.ot.2024.03.16.720p.mkv"
touch "$PROBLEM_PATTERNS_DIR/Tainstvennye.Istorii.e05.2023.1080p.mkv"

# Edge cases with mixed patterns
touch "$PROBLEM_PATTERNS_DIR/The.100.S01E01.1080p.mkv"  # "The 100" might be interpreted as movie from year 100
touch "$PROBLEM_PATTERNS_DIR/9-1-1.S02E03.720p.mkv"     # Hyphenated name with numbers
touch "$PROBLEM_PATTERNS_DIR/24.S01E01.1080p.mkv"       # Single number title

# Create a directory with multi-episode files
MULTI_EPISODE_DIR="$DOWNLOADS_DIR/multi_episode_files"
mkdir -p "$MULTI_EPISODE_DIR"
touch "$MULTI_EPISODE_DIR/Westworld.S01E01-E02.1080p.mkv"
touch "$MULTI_EPISODE_DIR/Succession.S03E01-02.720p.mkv"
touch "$MULTI_EPISODE_DIR/The.Last.of.Us.S01E01.E02.2160p.mkv"

# Create a README for the test environment
README_FILE="$TEST_DIR/README.md"
cat > "$README_FILE" << EOL
# JFMO Test Environment

This directory contains a comprehensive test environment for JFMO development with various file patterns.

## Pattern Categories

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

1. Files in "valid_patterns" directory should be detected and processed correctly
2. Files in "problematic_patterns" directory will likely have issues:
   - Some may be incorrectly categorized (movies as TV or vice versa)
   - Some may be skipped with error messages
   - Some might work correctly despite the complex patterns

This allows testing both the detection capabilities and the error handling of JFMO.
EOL

# Create directory info files for better organization
echo "These files follow standard patterns that JFMO should detect correctly" > "$VALID_PATTERNS_DIR/README.txt"
echo "These files follow non-standard patterns that may be problematic for JFMO to detect" > "$PROBLEM_PATTERNS_DIR/README.txt"
echo "Contains multi-episode files in various formats" > "$MULTI_EPISODE_DIR/README.txt"

echo ""
echo -e "${GREEN}✅ Comprehensive test environment created successfully!${NC}"
echo ""
echo -e "${YELLOW}To test JFMO, run:${NC}"
echo -e "${BLUE}python -m jfmo --config $CONFIG_FILE --test${NC}"
echo ""
echo -e "${YELLOW}For interactive testing with problematic patterns:${NC}"
echo -e "${BLUE}python -m jfmo --config $CONFIG_FILE${NC}"
echo ""
echo -e "${YELLOW}Test environment located at:${NC} $(pwd)/$TEST_DIR"
echo -e "${YELLOW}See $(pwd)/$TEST_DIR/README.md for details on test patterns${NC}"
echo ""