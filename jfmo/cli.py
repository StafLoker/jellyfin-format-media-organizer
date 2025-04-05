#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command-line interface for JFMO
"""

import argparse
import os
import sys
from . import __version__
from .config import Config
from .utils import Colors
from .utils.config_file import ConfigFileHandler


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Jellyfin Format Media Organizer - "
                    "A tool to organize media files according to Jellyfin's recommended format",
        epilog="Example: %(prog)s --test"
    )
    
    # Basic options
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--test", action="store_true", 
                        help="Run in test mode (no actual file changes)")
                        
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--quiet", action="store_true",
                        help="Suppress log messages (except errors)")
    output_group.add_argument("--verbose", action="store_true",
                        help="Show detailed log messages (default in test mode)")
                        
    # Interactive mode options (mutually exclusive)
    interactive_group = parser.add_mutually_exclusive_group()
    interactive_group.add_argument("--non-interactive", action="store_true",
                        help="Disable interactive mode (automatic selection of best match)")
    interactive_group.add_argument("--semi-interactive", action="store_true",
                        help="Only show interactive prompts for truly ambiguous matches")
    
    # Configuration file options
    config_group = parser.add_argument_group("Configuration File Options")
    config_group.add_argument("--config", metavar="FILE",
                             help="Path to configuration file")
    config_group.add_argument("--generate-config", metavar="FILE",
                             help="Generate a template configuration file")
    
    # Directory options
    dir_group = parser.add_argument_group("Directory Options")
    dir_group.add_argument("--media-dir", help="Base media directory", default=None)
    dir_group.add_argument("--downloads", help="Downloads directory", default=None)
    dir_group.add_argument("--films", help="Films directory", default=None)
    dir_group.add_argument("--series", help="TV Series directory", default=None)
    
    # File and permission options
    file_group = parser.add_argument_group("File and Permission Options")
    file_group.add_argument("--user", help="Media files owner username", default=None)
    file_group.add_argument("--group", help="Media files group", default=None)
    file_group.add_argument("--log", help="Log file path", default=None)
    
    # TMDB options
    tmdb_group = parser.add_argument_group("TMDB Integration Options")
    tmdb_group.add_argument("--tmdb-api-key", help="TMDB API key (or set TMDB_API_KEY environment variable)",
                          default=None)
    tmdb_group.add_argument("--disable-tmdb", action="store_true",
                          help="Disable TMDB integration")
    
    return parser.parse_args()


def handle_config_options(args):
    """Handle configuration file options"""
    # Check if we need to generate a template config
    if args.generate_config:
        if ConfigFileHandler.create_template(args.generate_config):
            print(f"Run with: jfmo --config {args.generate_config}")
            sys.exit(0)
        else:
            sys.exit(1)
    
    # Try to load config file - first from argument, then from default locations
    config_path = args.config or ConfigFileHandler.get_default_config_path()
    
    if config_path:
        ConfigFileHandler.update_config_from_file(config_path)


def update_config_from_args(args):
    """Update configuration from command line arguments (overriding any config file)"""
    # Update Test Mode
    Config.TEST_MODE = args.test
    
    # Update verbose mode based on test mode and explicit settings
    if args.quiet:
        Config.VERBOSE = False
    elif args.verbose:
        Config.VERBOSE = True
    else:
        Config.VERBOSE = args.test
    
    # Update interactive mode settings
    if args.non_interactive:
        Config.INTERACTIVE_MODE = False
        Config.SEMI_INTERACTIVE_MODE = False
    elif args.semi_interactive:
        Config.INTERACTIVE_MODE = True
        Config.SEMI_INTERACTIVE_MODE = True
    
    # Update paths if provided
    if args.media_dir:
        Config.MEDIA_DIR = args.media_dir
        
        # Only update derived paths if they weren't explicitly set
        if not args.downloads and not Config.DOWNLOADS.startswith("/"):
            Config.DOWNLOADS = os.path.join(Config.MEDIA_DIR, "downloads")
        if not args.films and not Config.FILMS.startswith("/"):
            Config.FILMS = os.path.join(Config.MEDIA_DIR, "films")
        if not args.series and not Config.SERIES.startswith("/"):
            Config.SERIES = os.path.join(Config.MEDIA_DIR, "series")
    
    # Update specific directories if provided
    if args.downloads:
        Config.DOWNLOADS = args.downloads
    if args.films:
        Config.FILMS = args.films
    if args.series:
        Config.SERIES = args.series
        
    # Update other settings
    if args.user:
        Config.MEDIA_USER = args.user
    if args.group:
        Config.MEDIA_GROUP = args.group
    if args.log:
        Config.LOG_FILE = args.log
        
    # Update TMDB settings
    if args.tmdb_api_key:
        Config.TMDB_API_KEY = args.tmdb_api_key
    if args.disable_tmdb:
        Config.TMDB_ENABLED = False


def check_root():
    """Check if running as root when not in test mode"""
    if not Config.TEST_MODE and os.geteuid() != 0:
        print(f"{Colors.RED}Error: This script must be run as root to set proper permissions{Colors.NC}")
        print(f"{Colors.YELLOW}Please run: sudo {sys.argv[0]} or use --test for a test run{Colors.NC}")
        sys.exit(1)


def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import transliterate
    except ImportError:
        print(f"{Colors.RED}Error: Required package 'transliterate' not found.{Colors.NC}")
        print(f"{Colors.YELLOW}Please install it using: pip install transliterate{Colors.NC}")
        sys.exit(1)
        
    if Config.TMDB_ENABLED:
        try:
            import requests
        except ImportError:
            print(f"{Colors.RED}Error: Required package 'requests' not found.{Colors.NC}")
            print(f"{Colors.YELLOW}Please install it using: pip install requests{Colors.NC}")
            sys.exit(1)