# JFMO - Jellyfin Format Media Organizer

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.6+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

JFMO is a powerful media organization tool designed to automatically structure and rename your media files according to Jellyfin's recommended naming conventions. It features automatic transliteration support for non-Latin alphabets and TMDB integration for accurate metadata.

## Features

- **Smart Media Detection** - Automatically identifies movies and TV shows
- **Proper Jellyfin Naming** - Renames files to Jellyfin's recommended format
- **TMDB Integration** - Adds TMDB IDs to filenames for better Jellyfin matching
- **Auto-Transliteration** - Converts transliterated names to their native scripts (Cyrillic, etc.)
- **Permissions Management** - Sets correct ownership and permissions for Jellyfin
- **Directory Structure** - Creates proper directory hierarchies for TV shows
- **Metadata Extraction** - Extracts year, quality, season/episode information
- **Directory Cleanup** - Removes empty directories after moving files
- **Test Mode** - Preview changes without modifying files

## Installation

### Prerequisites

- Python 3.6+
- `transliterate` package
- `requests` package (for TMDB integration)
- TMDB API key (optional, but recommended)

### Setting up a Virtual Environment

It's recommended to install JFMO in a virtual environment to avoid conflicts with other Python packages:

```bash
# Clone the repository
git clone https://github.com/StafLoker/jellyfin-format-media-organizer.git
cd jellyfin-format-media-organizer

# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip3 install transliterate requests

# Install JFMO in development mode
pip3 install -e .
```

To deactivate the virtual environment when you're done:
```bash
deactivate
```

### Installing Globally

If you prefer to install JFMO globally:

```bash
git clone https://github.com/StafLoker/jellyfin-format-media-organizer.git
cd jellyfin-format-media-organizer
pip install .
```

## TMDB Integration

JFMO can integrate with The Movie Database (TMDB) to add TMDB IDs to your media filenames, which helps Jellyfin match content more accurately.

### Setting up TMDB

1. Get an API key from [developers.themoviedb.org](https://developers.themoviedb.org)
2. Provide your API key in one of these ways:
   - Set the `TMDB_API_KEY` environment variable
   - Use the `--tmdb-api-key` command line option

### How TMDB Integration Works

When processing media files, JFMO will:
1. Search TMDB for the movie or TV show title
2. If found, extract the TMDB ID and correct release year
3. Add the TMDB ID to the filename in a format Jellyfin recognizes:
   - For movies: `Title (Year) [tmdbid-12345].mkv`
   - For series: `Series Name (Year) [tmdbid-67890]/Season 01/Series Name S01E01.mkv`

## Usage

### Basic Usage

Run in test mode first to see what changes would be made without modifying files:

```bash
# If installed in a virtual environment:
source venv/bin/activate  # On Windows: venv\Scripts\activate
jfmo --test

# Or if running directly from the repository:
python -m jfmo --test
```

When you're ready to make actual changes:

```bash
# Using sudo requires global installation or specifying the full path to the venv Python
sudo jfmo
# Or with TMDB API key:
sudo jfmo --tmdb-api-key YOUR_API_KEY
```

Root permissions are required to set proper file ownership.

### Command Line Options

```
Usage: jfmo [OPTIONS]

Options:
  --version               Show version and exit
  --test                  Run in test mode (no actual changes made)
  --quiet                 Suppress log messages
  -h, --help              Show this help message

Directory Options:
  --media-dir DIRECTORY   Base media directory (default: /data/media)
  --downloads DIRECTORY   Downloads directory
  --films DIRECTORY       Films directory
  --series DIRECTORY      TV series directory

File and Permission Options:
  --user USERNAME         Media files owner (default: jellyfin)
  --group GROUPNAME       Media files group (default: media)
  --log FILEPATH          Log file path

TMDB Integration Options:
  --tmdb-api-key KEY      TMDB API key
  --disable-tmdb          Disable TMDB integration
```

## Examples

### Before Organization

```
/data/media/downloads/
├── Severance.S02E02.1080p.rus.LostFilm.TV.mkv
├── Podslushano.v.Rybinske.S01.2024.SDR.WEB-DL.2160p/
├── The.Accountant.2.2024.2160p.HDTV.mkv
└── La Casa de Papel 3 - LostFilm.TV [1080p]/
    └── (various episode files)
```

### After Organization

```
/data/media/
├── films/
│   └── The Accountant 2 (2024) [tmdbid-717559] - [2160p].mkv
└── series/
    ├── La Casa de Papel (2017) [tmdbid-71446]/
    │   └── Season 03/
    │       ├── La Casa de Papel S03E01 - [1080p].mkv
    │       └── ...
    ├── Подслушано в Рыбинске (2024) [tmdbid-123456]/
    │   └── Season 01/
    │       ├── Подслушано в Рыбинске S01E01 - [2160p].mkv
    │       └── ...
    └── Severance (2022) [tmdbid-95396]/
        └── Season 02/
            ├── Severance S02E02 - [1080p].mkv
            └── ...
```

## Transliteration Support

JFMO automatically detects and converts transliterated text back to its original script. Supported languages:

- Russian
- Ukrainian
- Bulgarian
- Serbian
- Macedonian
- Greek
- Georgian
- Armenian
- Hebrew

## File Naming Convention

JFMO uses the following naming conventions:

### Movies
```
Title (Year) [tmdbid-ID] - [Quality].extension
```

### TV Series
```
Series Name (Year) [tmdbid-ID]/Season XX/Series Name SXXEXX - [Quality].extension
```

## Extending JFMO

JFMO is built with a modular architecture that makes it easy to extend:

```
jfmo/
├── detectors/       # Add new content detection algorithms
├── processors/      # Add new media processing methods
├── metadata/        # Add new metadata sources
└── utils/           # Add new utility functions
```

## Troubleshooting

- **Permission errors**: Make sure to run with `sudo` when not in test mode
- **Files not detected**: Check if your file naming patterns match JFMO's detection patterns
- **Transliteration issues**: Ensure the `transliterate` package is installed correctly
- **TMDB integration issues**: Verify your API key and internet connection
- **Check logs**: Examine `/tmp/jfmo.log` for detailed operation logs
- **Virtual environment issues**: If using sudo with a venv, make sure to use the full path to the Python interpreter in the venv

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Jellyfin Media Server](https://jellyfin.org/) for their naming recommendations
- [The Movie Database (TMDB)](https://www.themoviedb.org/) for their excellent API
- [transliterate](https://pypi.org/project/transliterate/) for multilingual support