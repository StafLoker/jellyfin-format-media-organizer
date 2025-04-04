#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Movie processor for JFMO
"""

import os
import re
from ..config import Config
from ..utils import FileOps, Colors, Logger
from ..metadata import TMDBClient
from .media_processor import MediaProcessor


class MovieProcessor(MediaProcessor):
    """Class for processing movie files"""
    
    def __init__(self):
        """Initialize the processor"""
        super().__init__()
        # Initialize TMDB client if enabled
        self.tmdb_client = TMDBClient() if Config.TMDB_ENABLED else None
    
    def get_tmdb_id(self, title, year=None):
        """
        Get TMDB ID for a movie
        
        Args:
            title (str): Movie title
            year (str, optional): Release year
            
        Returns:
            int or None: TMDB ID if found, None otherwise
        """
        if not self.tmdb_client or not Config.TMDB_ENABLED:
            return None
            
        movie = self.tmdb_client.search_movie(title, year)
        
        if movie:
            tmdb_id = movie.get('id')
            # Get year from TMDB if not provided
            if not year and 'release_date' in movie and movie['release_date']:
                year = movie['release_date'][:4]
                
            Logger.info(f"Found TMDB match for '{title}': ID {tmdb_id}, Year: {year}")
            return tmdb_id, year
            
        Logger.warning(f"No TMDB match found for movie: {title} {year if year else ''}")
        return None, year
    
    def process(self, file_path):
        """Process a movie file"""
        filename = os.path.basename(file_path)
        Logger.info(f"Processing movie: {filename}")
        
        # Clean movie name and get metadata
        base_title = self.get_clean_title(filename)
        year, quality = self.get_year_and_quality(filename)
        
        # Try to get TMDB ID and possibly more accurate year
        tmdb_id_info = (None, year)
        if Config.TMDB_ENABLED:
            print(f"{Colors.BLUE}Searching TMDB for:{Colors.NC} {base_title}")
            tmdb_id_info = self.get_tmdb_id(base_title, year)
        
        tmdb_id, year = tmdb_id_info
        
        # Remove year from title if it exists
        if year and year in base_title:
            base_title = re.sub(r'\s+' + re.escape(year), '', base_title).strip()
        
        # Format movie name with appropriate format
        extension = os.path.splitext(filename)[1]
        
        # Build the new filename with TMDB ID if available
        if year:
            if tmdb_id:
                if quality:
                    new_filename = f"{base_title} ({year}) [tmdbid-{tmdb_id}] - {quality}{extension}"
                else:
                    new_filename = f"{base_title} ({year}) [tmdbid-{tmdb_id}]{extension}"
            else:
                if quality:
                    new_filename = f"{base_title} ({year}) - {quality}{extension}"
                else:
                    new_filename = f"{base_title} ({year}){extension}"
        else:
            if tmdb_id:
                if quality:
                    new_filename = f"{base_title} [tmdbid-{tmdb_id}] - {quality}{extension}"
                else:
                    new_filename = f"{base_title} [tmdbid-{tmdb_id}]{extension}"
            else:
                if quality:
                    new_filename = f"{base_title} - {quality}{extension}"
                else:
                    new_filename = f"{base_title}{extension}"
        
        # Ensure films directory exists
        FileOps.ensure_dir(Config.FILMS)
        
        # Move file
        return FileOps.move_file(file_path, os.path.join(Config.FILMS, new_filename))