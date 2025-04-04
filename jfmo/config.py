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
    
    # Supported languages for transliteration
    TRANSLITERATION_LANGS = ['ru', 'uk', 'bg', 'mk', 'sr', 'el', 'ka', 'hy', 'he']
    
    # Video file extensions
    VIDEO_EXTENSIONS = ('.mkv', '.mp4', '.avi', '.m4v', '.mov', '.wmv', '.flv')
    
    # TMDB configuration
    TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '')
    TMDB_ENABLED = True
    
    @classmethod
    def update_from_args(cls, args):
        """Update configuration from command line arguments"""
        cls.TEST_MODE = args.test
        cls.VERBOSE = not args.quiet
        cls.INTERACTIVE_MODE = not args.non_interactive
        
        # Update paths if provided
        if args.media_dir:
            cls.MEDIA_DIR = args.media_dir
            
            # Only update derived paths if they weren't explicitly set
            if not args.downloads:
                cls.DOWNLOADS = os.path.join(cls.MEDIA_DIR, "downloads")
            if not args.films:
                cls.FILMS = os.path.join(cls.MEDIA_DIR, "films")
            if not args.series:
                cls.SERIES = os.path.join(cls.MEDIA_DIR, "series")
        
        # Update specific directories if provided
        if args.downloads:
            cls.DOWNLOADS = args.downloads
        if args.films:
            cls.FILMS = args.films
        if args.series:
            cls.SERIES = args.series
            
        # Update other settings
        if args.user:
            cls.MEDIA_USER = args.user
        if args.group:
            cls.MEDIA_GROUP = args.group
        if args.log:
            cls.LOG_FILE = args.log
            
        # Update TMDB settings
        if args.tmdb_api_key:
            cls.TMDB_API_KEY = args.tmdb_api_key
        if args.disable_tmdb:
            cls.TMDB_ENABLED = False