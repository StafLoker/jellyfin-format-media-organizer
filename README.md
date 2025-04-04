# Jellyfin Format Media Organizer

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Bash](https://img.shields.io/badge/language-bash-green.svg)

A powerful media organization tool designed to automatically structure and rename your media files according to Jellyfin's recommended naming conventions.

## Overview

This tool helps you organize your downloaded media files (movies and TV shows) by automatically:

- Detecting and categorizing content as either movies or TV series
- Cleaning file names (removing unnecessary tags, prefixes, etc.)
- Extracting relevant metadata (year, quality)
- Creating proper directory structures
- Renaming files to match Jellyfin's recommended format
- Handling special cases (series with numbered seasons in the title)

Perfect for maintaining a clean, consistent, and Jellyfin-friendly media library.

## Features

- **Smart Detection**: Identifies movies and TV shows based on filename patterns
- **Proper Formatting**:
  - Movies: `Title (Year) - [Quality].extension`
  - TV Shows: `Series Name (Year)/Season XX/Series Name SxxExx - [Quality].extension`
- **Metadata Extraction**: Automatically extracts year and quality information
- **Name Cleanup**: Removes unnecessary prefixes like `[NOOBDL]` and suffixes like `LostFilm.TV`
- **Multiple Patterns**: Recognizes various episode naming patterns (S01E01, S01.E01, etc.)
- **Special Cases**: Handles edge cases like `La Casa de Papel 3`
- **Safety First**: Offers both test mode and copy mode (instead of move) for safe operation
- **Detailed Logging**: Maintains comprehensive logs of all operations

## Requirements

- Bash shell environment
- Linux/Unix-based system
- Standard text processing utilities (sed, grep)

## Installation

1. Clone this repository or download the scripts:

```bash
git clone https://github.com/StafLoker/jellyfin-format-media-organizer.git
cd jellyfin-format-media-organizer
```

2. Make the scripts executable:

```bash
chmod +x jfmo_test.sh
chmod +x jfmo.sh
```

## Usage

### Step 1: Test Run (Recommended)

Always start with a test run to see what changes will be made without actually modifying any files:

```bash
./jfmo_test.sh
```

This will analyze your media files and show you a detailed report of how they would be organized.

### Step 2: Run the Organizer

When you're satisfied with the proposed changes, run the main script:

```bash
./jfmo.sh
```

If permission deny, use:

```bash
sudo bash -c './jfmo.sh'
```

By default, this will copy your files to their new locations (originals remain untouched).

## Configuration

Edit the scripts to customize their behavior:

### Basic Configuration

At the top of each script, you'll find variables you can modify:

```bash
# Base directories
MEDIA_DIR="/data/media"
DOWNLOADS="$MEDIA_DIR/downloads"
FILMS="$MEDIA_DIR/films"
SERIES="$MEDIA_DIR/series"

# CONFIGURATION
MOVE_FILES=false    # Set to true to move files instead of copying
VERBOSE=true        # Set to false for less detailed logs
LOG_FILE="/tmp/jellyfin_organizer.log"
```

## Directory Structure

The scripts expect and create the following directory structure:

```
/data/media/
├── downloads/    # Source directory with unorganized files
├── films/        # Destination for movies
└── series/       # Destination for TV shows
```

## Examples

### Before:
```
/data/media/downloads/
├── Severance.S02E02.1080p.rus.LostFilm.TV.mkv
├── The.Gorge.2025.2160p.SDR.mkv
└── La Casa de Papel 3 - LostFilm.TV [1080p]/
    └── (various episode files)
```

### After:
```
/data/media/
├── downloads/ (original files)
├── films/
│   └── The Gorge (2025) - [2160p].mkv
└── series/
    ├── La Casa de Papel/
    │   └── Season 03/
    │       ├── La Casa de Papel S03E01 - [1080p].mkv
    │       └── ...
    └── Severance/
        └── Season 02/
            ├── Severance S02E02 - [1080p].mkv
            └── ...
```

## Troubleshooting

- **Files not detected properly**: Check that they match one of the supported patterns
- **Permission issues**: Ensure the script has proper permissions to read/write in the directories
- **Log file**: Check the log file for detailed error information (`/tmp/jellyfin_organizer.log` by default)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Version History

- **1.0.0** (Initial Release)
  - Basic functionality for organizing movies and TV shows
  - Test mode for safe operation
  - Comprehensive pattern recognition for various file naming schemes