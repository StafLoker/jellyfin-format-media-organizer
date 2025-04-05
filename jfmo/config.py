#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration module for Jellyfin Format Media Organizer
"""

import os
from . import __version__


class Config:
    """Configuration class for JFMO"""
    # Version
    VERSION = __version__
    
    # Default paths
    MEDIA_DIR = "/data/media"
    DOWNLOADS = f"{MEDIA_DIR}/downloads"
    FILMS = f"{MEDIA_DIR}/films"
    SERIES = f"{MEDIA_DIR}/series"
    
    # File options
    LOG_FILE = "/tmp/jfmo.log"
    
    # User/permission settings
    MEDIA_USER = "jellyfin"
    MEDIA_GROUP = "media"
    
    # Runtime options
    TEST_MODE = False
    VERBOSE = True
    INTERACTIVE_MODE = True  # Enable interactive mode by default
    SEMI_INTERACTIVE_MODE = False  # Only show interactive prompt for truly ambiguous cases
    
    # Supported languages for transliteration
    TRANSLITERATION_LANGS = ['ru']
    
    # Video file extensions
    VIDEO_EXTENSIONS = ('.mkv', '.mp4', '.avi', '.m4v', '.mov', '.wmv', '.flv')
    
    # TMDB configuration
    TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '')
    TMDB_ENABLED = True