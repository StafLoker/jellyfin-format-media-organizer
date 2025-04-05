# JFMO - Jellyfin Format Media Organizer

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.6+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

JFMO is a powerful media organization tool designed to automatically structure and rename your media files according to Jellyfin's recommended naming conventions. It features automatic transliteration support for non-Latin alphabets and TMDB integration for accurate metadata.

## Features

- **Smart Media Detection** - Automatically identifies movies and TV shows
- **Proper Jellyfin Naming** - Renames files to Jellyfin's recommended format
- **TMDB Integration** - Adds TMDB IDs to filenames for better Jellyfin matching
- **Interactive Mode** - Helps you select the correct match when multiple options exist
- **Auto-Transliteration** - Converts transliterated names to their native scripts (Cyrillic, etc.)
- **Permissions Management** - Sets correct ownership and permissions for Jellyfin
- **Directory Structure** - Creates proper directory hierarchies for TV shows
- **Metadata Extraction** - Extracts year, quality, season/episode information
- **Directory Cleanup** - Removes empty directories after moving files
- **Test Mode** - Preview changes without modifying files
- **Configuration File** - Save your settings in a config file

## Installation

### Prerequisites

- Python 3.6+
- `transliterate` package
- `requests` package (for TMDB integration)
- TMDB API key (optional, but recommended)

### Recommended: Install with pipx

The easiest way to install and use JFMO is with [pipx](https://pypa.github.io/pipx/), which installs Python applications in isolated environments:

```bash
# Install pipx if you don't have it already
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install JFMO
pipx install git+https://github.com/StafLoker/jellyfin-format-media-organizer.git

# Now you can run JFMO from anywhere
jfmo --help
```

To update JFMO when new versions are available:

```bash
pipx upgrade jfmo
```

### Alternative: Setting up a Virtual Environment

If you prefer a virtual environment or are developing JFMO:

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

### Alternative: Installing Globally

If you prefer to install JFMO globally:

```bash
git clone https://github.com/StafLoker/jellyfin-format-media-organizer.git
cd jellyfin-format-media-organizer
pip3 install .
```

## Using JFMO with Root Permissions

Since JFMO needs to set proper file permissions, you'll need to run it with sudo when making actual changes. When installed with pipx, you can do this in two ways:

```bash
# Option 1: Use the full path to the pipx-installed executable
sudo $(which jfmo) --config ~/.config/jfmo/config.json

# Option 2: Use sudo with the Python module 
sudo -E $(pipx environment -v | grep PIPX_SHARED_LIBS | awk -F'"' '{print $2}')/bin/python -m jfmo --config ~/.config/jfmo/config.json
```

The `-E` flag preserves environment variables including your TMDB API key if set.

## Interactive Mode

JFMO features an interactive mode that helps you manually select the correct match when TMDB returns multiple possible results for a media file.

### How It Works

1. When JFMO finds multiple possible matches for a movie or TV show, it will present you with a list of options
2. For each option, it displays:
   - Title and year
   - TMDB ID
   - A brief overview (if available)
   - Popularity score
3. You can:
   - Select a match by number
   - Press Enter to select the recommended option
   - Skip the file (leave it untouched)
   - Quit the program

### Smart Selection

JFMO now features smarter selection algorithms that:
1. Prioritize exact title matches
2. Prioritize exact year matches
3. Consider popularity scores
4. Automatically select the best match when one is clearly superior

### Interactive Modes

JFMO offers three different interactive modes:

1. **Full Interactive Mode** (default): Shows selection options whenever multiple matches are found
2. **Semi-Interactive Mode** (`--semi-interactive`): Only shows selection options for truly ambiguous cases
3. **Non-Interactive Mode** (`--non-interactive`): Always selects the best match automatically

### Enabling/Disabling Interactive Mode

Interactive mode settings can be controlled in several ways:

1. **Command line**:
   - `--non-interactive` flag disables it completely
   - `--semi-interactive` flag enables smart selection
2. **Configuration file**:
   - Set `"interactive": false` to disable completely
   - Set `"semi_interactive": true` for smart selection
3. **Test mode**: Interactive mode still works during test runs

### Example Interactive Selection

```
============================================================
MULTIPLE MOVIE MATCHES FOUND
🔍 Original File: The.Matrix.1999.1080p.mkv
🔍 Search Query: The Matrix
============================================================
[1] (Recommend) The Matrix (1999) [tmdbid-603]
    Overview: Set in the 22nd century, The Matrix tells the story of a computer hacker who joins a group of underg...
    Popularity: 84.2
[2] Making 'The Matrix' (1999) [tmdbid-684431]
    Overview: A promotional making-of documentary for the film Matrix, The (1999) that devotes its time to explain...
    Popularity: 6.3
[3] The Matrix: What Is Bullet-Time? (1999) [tmdbid-684428]
    Overview: Special Effects wizard John Gaeta demonstrates how the "Bullet-Time" effects were created for the fi...
    Popularity: 2.1
------------------------------------------------------------
[s] Skip (leave file untouched)
[q] Quit
------------------------------------------------------------
Please select an option [1-3, s, q]: 
```

## Configuration

JFMO can be configured via command line arguments or through a configuration file.

### Configuration File

Using a configuration file is the recommended way to use JFMO, as it allows you to save your settings and avoid typing long command lines.

#### Generate a Template

First, generate a configuration template:

```bash
jfmo --generate-config ~/.config/jfmo/config.json
```

Edit the generated file to match your environment:

```json
{
    "directories": {
        "media_dir": "/data/media",
        "downloads": "/data/media/downloads",
        "films": "/data/media/films",
        "series": "/data/media/series"
    },
    "permissions": {
        "user": "jellyfin",
        "group": "media"
    },
    "tmdb": {
        "api_key": "your_tmdb_api_key_here",
        "enabled": true
    },
    "logging": {
        "log_file": "/tmp/jfmo.log",
        "verbose": false
    },
    "options": {
        "interactive": true,
        "semi_interactive": false
    }
}
```

#### Using the Configuration File

Once you have a configuration file, you can run JFMO with:

```bash
jfmo --config ~/.config/jfmo/config.json
```

JFMO will automatically look for configuration files in these locations (in order):
1. Custom path specified with `--config`
2. `~/.config/jfmo/config.json`
3. `/etc/jfmo/config.json`
4. `./config.json`

## TMDB Integration

JFMO can integrate with The Movie Database (TMDB) to add TMDB IDs to your media filenames, which helps Jellyfin match content more accurately.

### Setting up TMDB

1. Get an API key from [developers.themoviedb.org](https://developers.themoviedb.org)
2. Provide your API key in one of these ways:
   - Set the `TMDB_API_KEY` environment variable
   - Use the `--tmdb-api-key` command line option
   - Add it to your configuration file in the "tmdb" section

### How TMDB Integration Works

When processing media files, JFMO will:
1. Search TMDB for the movie or TV show title
2. If found, extract the TMDB ID and correct release year
3. If multiple matches are found, use interactive mode to let you choose
4. Add the TMDB ID to the filename in a format Jellyfin recognizes:
   - For movies: `Title (Year) [tmdbid-12345].mkv`
   - For series: `Series Name (Year) [tmdbid-67890]/Season 01/Series Name S01E01.mkv`

## Usage

### Basic Usage

Run in test mode first to see what changes would be made without modifying files:

```bash
# With a configuration file:
jfmo --config ~/.config/jfmo/config.json --test

# Or with default configuration locations:
jfmo --test
```

When you're ready to make actual changes:

```bash
# Using sudo with explicit config path
sudo $(which jfmo) --config ~/.config/jfmo/config.json
```

Root permissions are required to set proper file ownership.

### Command Line Options

```
Usage: jfmo [OPTIONS]

Options:
  --version               Show version and exit
  --test                  Run in test mode (no actual changes made)
  --verbose               Show detailed log messages (default in test mode)
  --quiet                 Suppress log messages
  -h, --help              Show this help message

Interactive Mode Options:
  --non-interactive       Disable interactive mode (automatic selection of best match)
  --semi-interactive      Only show interactive prompts for truly ambiguous matches

Configuration File Options:
  --config FILE           Path to configuration file
  --generate-config FILE  Generate a template configuration file

Directory Options:
  --media-dir DIRECTORY   Base media directory
  --downloads DIRECTORY   Downloads directory
  --films DIRECTORY       Films directory
  --series DIRECTORY      TV series directory

File and Permission Options:
  --user USERNAME         Media files owner
  --group GROUPNAME       Media files group
  --log FILEPATH          Log file path

TMDB Integration Options:
  --tmdb-api-key KEY      TMDB API key
  --disable-tmdb          Disable TMDB integration
```

## Development and Testing

JFMO includes a development script to set up a test environment for easy testing and development.


### Project Structure

```
jfmo/
├── __init__.py                # Package initialization and version
├── __main__.py                # Main entry point
├── cli.py                     # Command-line interface
├── config.py                  # Configuration handler
├── detectors/                 # Media detection modules
│   ├── __init__.py
│   ├── quality.py             # Quality detection
│   ├── season_episode.py      # TV show season/episode detection
│   └── year.py                # Year detection
├── metadata/                  # Metadata providers
│   ├── __init__.py
│   └── tmdb.py                # TMDB integration
├── processors/                # Media processors
│   ├── __init__.py
│   ├── media_processor.py     # Base processor class
│   ├── movie_processor.py     # Movie processing
│   ├── series_processor.py    # TV series processing
│   └── directory_processor.py # Directory processing
└── utils/                     # Utility modules
    ├── __init__.py
    ├── colors.py              # Terminal colors
    ├── config_file.py         # Config file handling
    ├── file_ops.py            # File operations
    ├── interactive_ui.py      # Interactive UI
    ├── logger.py              # Logging
    ├── output_formatter.py    # Output formatting
    └── transliteration.py     # Transliteration support
```

### Setting up a Test Environment

```bash
# Make the script executable
chmod +x dev/setup_test_env.sh

# Run the script to create a test environment
./dev/setup_test_env.sh
```

This will create a `test_environment` directory with:
- Sample movie files
- Sample TV show files and directories
- Test configuration with your current user permissions
- Directory structure for testing

### Using the Test Environment

The test script will output commands to run JFMO with the test environment:

```bash
# Run in test mode (no actual changes)
python3 -m jfmo --config ./test_environment/config/jfmo_test_config.json --test

# Run with actual changes
python3 -m jfmo --config ./test_environment/config/jfmo_test_config.json
```

Since the test environment uses your current user, you don't need to use `sudo` for testing.

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

JFMO automatically detects and converts Russian transliterated text back to Cyrillic script. It uses an advanced linguistic algorithm to identify potentially Russian filenames by looking for:

1. Russian functional words in transliteration (v, na, ot, etc.)
2. Phonetic patterns common in Russian (zh, shch, ya, etc.)
3. Unusual word length and character patterns
4. Letter frequency unusual in English but common in transliterated Russian
5. Specific Russian terms common in media filenames
6. Russian grammatical endings (-yj, -aya, etc.)

This allows for accurate conversion of filenames like:
- "Podslushano.v.Rybinske" → "Подслушано.в.Рыбинске"
- "Tainstvennye.Istorii" → "Таинственные.Истории"

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
- **Check logs**: Examine the log file for detailed operation logs
- **Configuration file issues**: Make sure your JSON file is valid
- **pipx issues**: Try reinstalling with `pipx uninstall jfmo` followed by `pipx install jfmo`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Jellyfin Media Server](https://jellyfin.org/) for their naming recommendations
- [The Movie Database (TMDB)](https://www.themoviedb.org/) for their excellent API
- [transliterate](https://pypi.org/project/transliterate/) for multilingual support