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
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress log messages (except errors)")
    
    # Directory options
    dir_group = parser.add_argument_group("Directory Options")
    dir_group.add_argument("--media-dir", help="Base media directory", default=Config.MEDIA_DIR)
    dir_group.add_argument("--downloads", help="Downloads directory", default=None)
    dir_group.add_argument("--films", help="Films directory", default=None)
    dir_group.add_argument("--series", help="TV Series directory", default=None)
    
    # File and permission options
    file_group = parser.add_argument_group("File and Permission Options")
    file_group.add_argument("--user", help="Media files owner username", default=Config.MEDIA_USER)
    file_group.add_argument("--group", help="Media files group", default=Config.MEDIA_GROUP)
    file_group.add_argument("--log", help="Log file path", default=Config.LOG_FILE)
    
    # TMDB options
    tmdb_group = parser.add_argument_group("TMDB Integration Options")
    tmdb_group.add_argument("--tmdb-api-key", help="TMDB API key (or set TMDB_API_KEY environment variable)",
                          default=Config.TMDB_API_KEY)
    tmdb_group.add_argument("--disable-tmdb", action="store_true",
                          help="Disable TMDB integration")
    
    return parser.parse_args()


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