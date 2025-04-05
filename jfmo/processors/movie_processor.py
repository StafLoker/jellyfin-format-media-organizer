#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Movie processor for JFMO
"""

import os
import re
from ..config import Config
from ..utils import FileOps, Colors, Logger, Transliterator
from ..utils.output_formatter import OutputFormatter
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
            OutputFormatter.print_file_processing_info("TMDB Match", f"ID: {tmdb_id}, Year: {year}")
            return tmdb_id, year
            
        Logger.warning(f"No TMDB match found for movie: {title} {year if year else ''}")
        OutputFormatter.print_file_processing_info("TMDB", "No match found")
        return None, year
    
    def process(self, file_path):
        """Process a movie file"""
        filename = os.path.basename(file_path)
        
        Logger.info(f"Processing movie: {filename}")
        
        numeric_movie_match = re.match(r'^([12][0-9]{3})\.', filename)
        numeric_movie_name = None
        if numeric_movie_match:
            numeric_movie_name = numeric_movie_match.group(1)
            
        # Clean movie name
        clean_title = self.get_clean_title(filename)
        
        if numeric_movie_name and (not clean_title.strip() or 
                                 clean_title.strip() == "A Space Odyssey"):
            clean_title = f"{numeric_movie_name} {clean_title}"
            
        # Get a clean name without all the metadata
        base_title = clean_title
        
        OutputFormatter.print_file_processing_info("Title", base_title)
        
        # Try to transliterate BEFORE getting metadata
        original_title = base_title
        base_title = Transliterator.transliterate_text(base_title)
        if original_title != base_title:
            OutputFormatter.print_file_processing_info("Transliteration", f"{original_title} → {base_title}")
        
        # Now get year and quality from the original filename
        year, quality = self.get_year_and_quality(filename)
        
        if year:
            OutputFormatter.print_file_processing_info("Year", year)
        if quality:
            OutputFormatter.print_file_processing_info("Quality", quality)
        
        # Try to get TMDB ID and possibly more accurate year
        tmdb_id_info = (None, year)
        if Config.TMDB_ENABLED:
            OutputFormatter.print_file_processing_info("TMDB Search", base_title)
            tmdb_id_info = self.get_tmdb_id(base_title, year, filename)
        
        # If user skipped in interactive mode, don't process the file
        if tmdb_id_info is None and Config.INTERACTIVE_MODE:
            OutputFormatter.print_file_processing_result(
                success=False,
                message="Skipped by user. File will not be processed."
            )
            return False
            
        tmdb_id, year = tmdb_id_info if tmdb_id_info else (None, year)
        
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
        OutputFormatter.print_file_processing_info("New Filename", new_filename)
        OutputFormatter.print_file_processing_info("Destination", destination)
        
        # Move file
        result = FileOps.move_file(file_path, destination)
        
        # Display result
        OutputFormatter.print_file_processing_result(
            success=result,
            message="Movie processed successfully" if result else "Failed to process movie",
            details={
                "From": file_path,
                "To": destination
            }
        )
        
        return result