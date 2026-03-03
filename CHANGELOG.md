# Changelog

All notable changes to Jellyfin Format Media Organizer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-03-03

### Added
- Pipeline-based parser with individual steps (extension, season/episode, year, quality, media type, title, ...)
- Dependency injection container for service management
- Token formatter for flexible pattern-based file naming
- N-gram language detection
- Daemon mode for background media organization
- Docker deployment support
- Comprehensive test suite
- Release workflow automation for PyPI and Docker builds
- User-friendly output formatting for manual runs

### Changed
- Migrated to `uv` package manager from pip
- Simplified processors architecture
- Reduced code complexity throughout codebase

### Fixed
- Permission troubles in file operations

## [2.0.0] - 2025-04-05

### Added
- Three interactive modes:
  - Full Interactive Mode (default): Comprehensive match selection
  - Semi-Interactive Mode: Smart selection for truly ambiguous cases
  - Non-Interactive Mode: Automatic best match selection
- Smart selection algorithms with exact title/year matching and popularity score consideration
- Flexible configuration options with multiple file locations and templates
- Advanced transliteration support for non-Latin alphabets
- Automatic conversion of transliterated names to native scripts
- Better handling of Russian and other Cyrillic content
- Installation and upgrade via pipx
- Configuration template generation
- Granular control over TMDB and interactive mode settings

### Changed
- TMDB integration refinements with improved metadata extraction and filename formatting
- More accurate TMDB ID integration for both movies and TV shows
- Enhanced matching algorithm for media content
- Modular architecture for easier extensibility
- Improved detection algorithms for movies and TV shows
- Enhanced metadata extraction capabilities
- Better logging and error handling
- Smarter media type detection
- Improved quality and metadata extraction
- More accurate season and episode identification
- Refined directory structure creation
- Enhanced permissions management
- Improved empty directory cleanup
- More robust file naming conventions
- Centralized configuration management with environment-specific settings

## [1.0.0] - 2025-04-04

### Added
- Smart detection: Identifies movies and TV shows based on filename patterns
- Proper formatting:
  - Movies: `Title (Year) - [Quality].extension`
  - TV Shows: `Series Name (Year)/Season XX/Series Name SxxExx - [Quality].extension`
- Metadata extraction: Automatically extracts year and quality information
- Name cleanup: Removes unnecessary prefixes like `[NOOBDL]` and suffixes like `LostFilm.TV`
- Multiple patterns: Recognizes various episode naming patterns (S01E01, S01.E01, etc.)
- Special cases: Handles edge cases like `La Casa de Papal 3`
- Proper permissions: Sets correct ownership (`jellyfin:media`) and permissions for all processed files
- Directory cleanup: Automatically removes empty directories after files are moved
- Detailed logging: Maintains comprehensive logs of all operations
