<div align="center">
   <img width="150" height="150" src="logo.png" alt="Logo">
   <h1><b>Jellyfin Format Media Organizer</b></h1>
   <p><i>~ JFMO ~</i></p>
   <p align="center">
      <a href="https://github.com/StafLoker/jellyfin-format-media-organizer/wiki">Docs</a> ·
      <a href="https://github.com/StafLoker/jellyfin-format-media-organizer/blob/main/LICENSE">License</a> ·
      <a href="https://github.com/StafLoker/jellyfin-format-media-organizer/releases">Releases</a>
   </p>
</div>

<div align="center">
   <a href="https://github.com/StafLoker/jellyfin-format-media-organizer/releases"><img src="https://img.shields.io/github/downloads/StafLoker/jellyfin-format-media-organizer/total.svg?style=flat" alt="downloads"/></a>
   <a href="https://github.com/StafLoker/jellyfin-format-media-organizer/releases"><img src="https://img.shields.io/github/release-pre/StafLoker/jellyfin-format-media-organizer.svg?style=flat" alt="latest version"/></a>

   <p>JFMO is a powerful media organization tool designed to automatically structure and rename your media files according to Jellyfin's recommended naming conventions. It features automatic transliteration support for non-Latin alphabets and TMDB integration for accurate metadata.</p>
</div>

!!!!!!!!!!!!!!TEMP - DATASET LINK: https://www.kaggle.com/datasets/stafloker/media-transliterated

!!!!!!!!!!!!!!! Model accuracy 93%

!!!!!!!!! Inspired by [Language Identification for Texts Written in Transliteration](https://ceur-ws.org/Vol-871/paper_2.pdf).

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
- TMDB API key (optional, but recommended)

### Quick Install & Upgrade

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

JFMO automatically detects and converts Russian transliterated text back to Cyrillic script.

This allows for accurate conversion of filenames like:
- "Podslushano v Rybinske" → "Подслушано в Рыбинске"
- "Tainstvennye Istorii" → "Таинственные Истории"

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

## Troubleshooting

- **Permission errors**: Make sure to run with `sudo` when not in test mode
- **Files not detected**: Check if your file naming patterns match JFMO's detection patterns
- **Transliteration issues**: Ensure the `transliterate` package is installed correctly
- **TMDB integration issues**: Verify your API key and internet connection
- **Check logs**: Examine the log file for detailed operation logs
- **Configuration file issues**: Make sure your JSON file is valid
- **pipx issues**: Try reinstalling with `pipx uninstall jfmo` followed by `pipx install jfmo`

## Acknowledgments

- [Jellyfin Media Server](https://jellyfin.org/) for their naming recommendations
- [The Movie Database (TMDB)](https://www.themoviedb.org/) for their excellent API
- [transliterate](https://pypi.org/project/transliterate/) for multilingual support
