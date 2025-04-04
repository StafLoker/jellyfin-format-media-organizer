#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Movie processor for JFMO
"""

import os
import re
from ..config import Config
from ..utils import FileOps, Colors, Logger
from ..utils.interactive_ui import InteractiveUI
from ..metadata import TMDBClient
from .media_processor import MediaProcessor


class MovieProcessor(MediaProcessor):
    """Class for processing movie files"""
    
    def __init__(self):
        """Initialize the processor"""
        super().__init__()
        # Initialize TMDB client if enabled
        self.tmdb_client = TMDBClient(interactive=Config.INTERACTIVE_MODE) if Config.TMDB_ENABLED else None
    
    def get_tmdb_id(self, title, year=None, filename=None):
        """
        Get TMDB ID for a movie
        
        Args:
            title (str): Movie title
            year (str, optional): Release year
            filename (str, optional): Original filename for interactive mode
            
        Returns:
            tuple: (tmdb_id, year) if found, (None, original_year) otherwise
        """
        if not self.tmdb_client or not Config.TMDB_ENABLED:
            return None, year
            
        movie = self.tmdb_client.search_movie(title, year, filename)
        
        if movie:
            tmdb_id = movie.get('id')
            # Get year from TMDB if not provided or if we have more accurate info
            if 'release_date' in movie and movie['release_date']:
                year = movie['release_date'][:4]
                
            Logger.info(f"Found TMDB match for '{title}': ID {tmdb_id}, Year: {year}")
            return tmdb_id, year
            
        Logger.warning(f"No TMDB match found for movie: {title} {year if year else ''}")
        return None, year
    
    def process(self, file_path):
        """Process a movie file"""
        filename = os.path.basename(file_path)
        
        # Display processing header
        action = "Testing (no changes)" if Config.TEST_MODE else "Moving and renaming"
        InteractiveUI.display_processing_header(filename, "movie", action)
        
        Logger.info(f"Processing movie: {filename}")
        
        # Clean movie name and get metadata
        base_title = self.get_clean_title(filename)
        year, quality = self.get_year_and_quality(filename)
        
        # Try to get TMDB ID and possibly more accurate year
        tmdb_id_info = (None, year)
        if Config.TMDB_ENABLED:
            print(f"{Colors.BLUE}Searching TMDB for:{Colors.NC} {base_title}")
            tmdb_id_info = self.get_tmdb_id(base_title, year, filename)
        
        # If user skipped in interactive mode, don't process the file
        if tmdb_id_info is None and Config.INTERACTIVE_MODE:
            print(f"{Colors.YELLOW}Skipped by user. File will not be processed.{Colors.NC}")
            return False
            
        tmdb_id, year = tmdb_id_info if tmdb_id_info else (None, year)
        
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
        
        # Display what we're going to do
        destination = os.path.join(Config.FILMS, new_filename)
        print(f"{Colors.GREEN}Movie identified:{Colors.NC} {base_title} ({year or 'Unknown Year'})")
        if tmdb_id:
            print(f"{Colors.GREEN}TMDB ID:{Colors.NC} {tmdb_id}")
        print(f"{Colors.GREEN}New filename:{Colors.NC} {new_filename}")
        
        # Move file
        result = FileOps.move_file(file_path, destination)
        
        # Display result
        InteractiveUI.display_result(
            success=result,
            message="Movie processed successfully" if result else "Failed to process movie",
            original_path=file_path,
            destination_path=destination
        )
        
        return result