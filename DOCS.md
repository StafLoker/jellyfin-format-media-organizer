# Jellyfin Format Media Organizer (JFMO)

A powerful Python tool to automatically organize media files according to Jellyfin's recommended naming conventions, with intelligent transliteration detection, TMDB integration, and daemon mode support.

## Features

- **Automatic Media Organization**: Organizes movies and TV series into Jellyfin-compatible directory structures
- **Intelligent Transliteration Detection**: Advanced N-gram probabilistic model to detect and transliterate Russian text written in Latin characters (93% accuracy)
- **TMDB Integration**: Fetches accurate metadata, release years, and IDs from The Movie Database
- **Interactive Mode**: Handles ambiguous matches with user-friendly selection prompts
- **Daemon Mode**: Continuous monitoring of download directories for automatic processing
- **YAML Configuration**: Flexible configuration file support
- **Incomplete Episode Detection**: Prevents partial season moves when downloads are incomplete
- **Test Mode**: Preview changes without actually moving files

## Installation

### Requirements

- Python 3.9 or higher
- Required packages: `pyyaml`, `transliterate`, `requests`

### Install via pip

```bash
pip install jfmo
```

### Install from source

```bash
git clone https://github.com/StafLoker/jellyfin-format-media-organizer.git
cd jellyfin-format-media-organizer
pip install -e .
```

## Quick Start

### Generate Configuration File

```bash
jfmo --generate-config ~/.config/jfmo/config.yaml
```

### Edit Configuration

Edit the generated config file and set your directories and TMDB API key:

```yaml
# JFMO Configuration File
directories:
  media_dir: /data/media
  downloads: /data/media/downloads
  films: /data/media/films
  series: /data/media/series
  incomplete: /data/media/incomplete  # Optional

permissions:
  user: jellyfin
  group: media

tmdb:
  api_key: "your_tmdb_api_key_here"  # Get from https://www.themoviedb.org/settings/api
  enabled: true

logging:
  log_file: /var/log/jfmo.log
  verbose: false

options:
  interactive: true

daemon:
  enabled: false
  check_interval: 10
```

### Run JFMO

```bash
# Test mode (no changes)
jfmo --config ~/.config/jfmo/config.yaml --test --verbose

# Manual mode (one-time execution)
sudo jfmo --config ~/.config/jfmo/config.yaml

# Daemon mode (continuous monitoring)
sudo jfmo --daemon --config ~/.config/jfmo/config.yaml
```

## Usage

### Command Line Options

```
Basic Options:
  --version              Show version information
  --test                 Test mode - no actual file operations
  --quiet                Suppress log messages (except errors)
  --verbose              Show detailed log messages
  --no-interactive       Disable interactive mode (automatic selection)

Daemon Mode:
  -d, --daemon           Run in daemon mode (watch directory for new files)
  --daemon-interval N    Check interval in seconds (default: 10)
  --incomplete-dir DIR   Directory with incomplete downloads

Manual Mode:
  -m, --manual           Manual mode - single execution with interactive prompts

Configuration:
  --config FILE          Path to configuration file
  --generate-config FILE Generate template configuration file

Directories:
  --media-dir DIR        Base media directory
  --downloads DIR        Downloads directory
  --films DIR            Films directory
  --series DIR           TV series directory

Permissions:
  --user USER            Media files owner username
  --group GROUP          Media files group

TMDB Integration:
  --tmdb-api-key KEY     TMDB API key (or set TMDB_API_KEY env var)
  --disable-tmdb         Disable TMDB integration

Logging:
  --log FILE             Log file path
```

### Examples

**Test mode with verbose output:**
```bash
jfmo --config config.yaml --test --verbose
```

**Manual mode with specific directories:**
```bash
sudo jfmo --downloads /mnt/downloads --films /mnt/movies --series /mnt/tv
```

**Daemon mode with incomplete directory:**
```bash
sudo jfmo --daemon --incomplete-dir /mnt/incomplete --daemon-interval 30
```

**Non-interactive mode (automatic):**
```bash
sudo jfmo --config config.yaml --no-interactive
```

## Naming Conventions

### Movies

**Input:**
```
The.Matrix.1999.1080p.mkv
Inception.2010.2160p.mkv
```

**Output:**
```
/films/The Matrix (1999) [tmdbid-603] - [1080p].mkv
/films/Inception (2010) [tmdbid-27205] - [2160p].mkv
```

### TV Series

**Input:**
```
Severance.S01E01.1080p.mkv
Breaking.Bad.S01.E01.720p.mkv
Game.of.Thrones.3x07.1080p.mkv
```

**Output:**
```
/series/Severance (2022) [tmdbid-95396]/Season 01/Severance S01E01 - [1080p].mkv
/series/Breaking Bad (2008) [tmdbid-1396]/Season 01/Breaking Bad S01E01 - [720p].mkv
/series/Game of Thrones (2011) [tmdbid-1399]/Season 03/Game of Thrones S03E07 - [1080p].mkv
```

## Transliteration Detection

JFMO uses an advanced **N-gram probabilistic model** to detect Russian text written in Latin characters (transliteration) and convert it back to proper Cyrillic script.

### How It Works

The system employs a 3-gram language model trained on real-world media filenames to classify text as Russian or English with **93% accuracy**. This approach is inspired by the research paper [_"Language Identification for Texts Written in Transliteration"_](https://ceur-ws.org/Vol-871/paper_2.pdf).

### Training Dataset

The model was trained on a specialized dataset available at:
**[Media Transliterated Dataset on Kaggle](https://www.kaggle.com/datasets/stafloker/media-transliterated)**

### Example Transliterations

**Input:**
```
Podslushano.v.Rybinske.S01E01.2160p.mkv
```

**Detected as Russian → Transliterated:**
```
/series/Подслушано в Рыбинске (2024) [tmdbid-xxxxx]/Season 01/Подслушано в Рыбинске S01E01 - [2160p].mkv
```

The model successfully handles:
- Russian series and movie names written in Latin characters
- Mixed content (English titles with Russian subtitles)
- Edge cases with numbers and special characters

## TMDB Integration

### Features

- **Automatic Metadata Retrieval**: Fetches accurate titles, release years, and IDs
- **Interactive Selection**: When multiple matches found, presents options to user
- **Caching**: Reduces API calls by caching series/movie lookups
- **Popularity Ranking**: Suggests most likely match based on popularity scores

### Getting a TMDB API Key

1. Create account at [The Movie Database](https://www.themoviedb.org/)
2. Go to Settings → API
3. Request API key (free for personal use)
4. Add to config file or use `--tmdb-api-key` flag

### Interactive Mode Example

```
═══════════════════════════════════════════════════════════════
MULTIPLE MOVIE MATCHES FOUND
Original File: The.Thing.2011.1080p.mkv
Search Query: The Thing
═══════════════════════════════════════════════════════════════
[1] (Recommend) The Thing (2011) [tmdbid-8452]
    Overview: Paleontologist Kate Lloyd is invited to join a Norwegian...
    Popularity: 45.2

[2] The Thing (1982) [tmdbid-1091]
    Overview: Scientists in the Antarctic are confronted by a shape-shifting...
    Popularity: 78.5

───────────────────────────────────────────────────────────────
[s] Skip (leave file untouched)
[q] Quit
───────────────────────────────────────────────────────────────
Please select an option [1-2, s, q]:
```

## Daemon Mode

Daemon mode enables continuous monitoring of your downloads directory for automatic processing.

### Features

- **Automatic Processing**: Monitors directory and processes new files as they appear
- **File Stability Check**: Waits for files to finish downloading before processing
- **Incomplete Episode Detection**: Skips processing if incomplete episodes exist
- **Minimal Output**: Clean, concise logging suitable for background operation
- **Signal Handling**: Graceful shutdown on SIGINT/SIGTERM

### Usage

```bash
# Start daemon
sudo jfmo --daemon --config /etc/jfmo/config.yaml

# With custom check interval (30 seconds)
sudo jfmo --daemon --daemon-interval 30

# With incomplete directory
sudo jfmo --daemon --incomplete-dir /mnt/incomplete
```

### Systemd Service

Create `/etc/systemd/system/jfmo.service`:

```ini
[Unit]
Description=JFMO Media Organizer Daemon
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/jfmo --daemon --config /etc/jfmo/config.yaml
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable jfmo
sudo systemctl start jfmo
sudo systemctl status jfmo
```

## Supported Patterns

### Series Patterns

- `SxxExx` - Severance.S01E01.1080p.mkv
- `S01.E01` - Breaking.Bad.S01.E01.720p.mkv
- `sXXeXX` - friends.s01e01.720p.mkv
- `NxNN` - Game.of.Thrones.3x07.1080p.mkv
- `Multi-episode` - Westworld.S01E01-E02.1080p.mkv
- `Combined` - Breaking.Bad.401.720p.mkv (S04E01)

### Movie Patterns

- `Title.Year.Quality` - The.Matrix.1999.1080p.mkv
- `Title (Year) Quality` - Inception (2010) 2160p.mkv
- `Title_Year_Quality` - Interstellar_2014_720p.mp4

### Quality Detection

Supports: 480p, 720p, 1080p, 1440p, 2160p (4K), 4320p (8K), SD, HD, FHD, UHD, HDR

## Incomplete Episode Detection

JFMO can detect incomplete episode downloads and prevent partial season moves.

```bash
# Specify incomplete directory
jfmo --incomplete-dir /mnt/incomplete --daemon

# Or in config file
directories:
  incomplete: /mnt/incomplete
```

When processing series, JFMO checks if episodes from the same season exist in the incomplete directory and skips processing if found.

## Configuration File

JFMO supports YAML configuration files for persistent settings.

### Default Locations

JFMO searches for config files in this order:
1. `~/.config/jfmo/config.yaml`
2. `~/.config/jfmo/config.yml`
3. `/etc/jfmo/config.yaml`
4. `/etc/jfmo/config.yml`
5. `./config.yaml`
6. `./config.yml`

### Full Configuration Example

```yaml
# Directory Configuration
directories:
  media_dir: /data/media
  downloads: /data/media/downloads
  films: /data/media/films
  series: /data/media/series
  incomplete: /data/media/incomplete

# File Permissions
permissions:
  user: jellyfin
  group: media

# TMDB Integration
tmdb:
  api_key: "your_api_key_here"
  enabled: true

# Logging Configuration
logging:
  log_file: /var/log/jfmo.log
  verbose: false

# Processing Options
options:
  interactive: true  # Auto-disabled in daemon mode

# Daemon Mode Options
daemon:
  enabled: false
  check_interval: 10  # seconds
```

## Test Environment

JFMO includes a comprehensive test environment setup script:

```bash
# Run the setup script
bash setup_test_env.sh

# Test with the environment
jfmo --config ./test_environment/config/jfmo_test_config.yaml --test --verbose
```

The test environment creates:
- Sample movie files with various naming patterns
- Sample TV series files with different episode formats
- Edge cases and problematic patterns
- Configuration file for testing

## Troubleshooting

### Permission Errors

Run with `sudo` for proper file ownership:
```bash
sudo jfmo --config config.yaml
```

Or use `--test` mode to preview without changes:
```bash
jfmo --config config.yaml --test
```

### TMDB API Issues

```bash
# Disable TMDB if having connection issues
jfmo --config config.yaml --disable-tmdb

# Or set in config file
tmdb:
  enabled: false
```

### Transliteration Not Working

Ensure language models are present in `models/` directory:
- `jfmo_russian_model.pkl`
- `jfmo_english_model.pkl`

Models are included with the package installation.

### Daemon Not Processing Files

Check:
1. File stability - daemon waits for files to finish downloading
2. Incomplete directory - files may be skipped if incomplete episodes exist
3. Permissions - daemon must run as root/sudo
4. Log file - check `log_file` setting for detailed logs

## Development

### Project Structure

```
jfmo/
├── __init__.py
├── __main__.py           # Main entry point
├── cli.py                # Command line interface
├── config.py             # Configuration management
├── daemon.py             # Daemon mode implementation
├── detectors/            # Pattern detection
│   ├── season_episode.py
│   ├── year.py
│   └── quality.py
├── metadata/             # TMDB integration
│   └── tmdb.py
├── processors/           # File processors
│   ├── movie_processor.py
│   ├── series_processor.py
│   └── directory_processor.py
└── utils/                # Utilities
    ├── colors.py
    ├── config_file.py
    ├── file_ops.py
    ├── interactive_ui.py
    ├── logger.py
    ├── output_formatter.py
    └── transliteration.py
```

### Running Tests

```bash
# Setup test environment
bash setup_test_env.sh

# Run in test mode
jfmo --config ./test_environment/config/jfmo_test_config.yaml --test --verbose
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Credits

- **Transliteration Detection**: Inspired by [_"Language Identification for Texts Written in Transliteration"_](https://ceur-ws.org/Vol-871/paper_2.pdf)
- **Training Dataset**: [Media Transliterated Dataset on Kaggle](https://www.kaggle.com/datasets/stafloker/media-transliterated)
- **TMDB**: Movie and TV show metadata provided by [The Movie Database](https://www.themoviedb.org/)
- **Jellyfin**: Naming conventions based on [Jellyfin Documentation](https://jellyfin.org/docs/)

## Support

- **Issues**: [GitHub Issues](https://github.com/StafLoker/jellyfin-format-media-organizer/issues)
- **Documentation**: [GitHub Wiki](https://github.com/StafLoker/jellyfin-format-media-organizer/wiki)

## Changelog

### Version 3.0.0
- Added daemon mode for continuous monitoring
- Implemented YAML configuration file support
- Advanced N-gram transliteration detection (93% accuracy)
- Interactive TMDB match selection
- Incomplete episode detection
- Improved error handling and logging
- Systemd service support

### Version 2.0.0
- TMDB integration
- Basic transliteration support
- Interactive mode

### Version 1.0.0
- Initial release
- Basic file organization
- Movie and TV series support