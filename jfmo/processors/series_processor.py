#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Series processor for JFMO
"""

import os
import re
from ..config import Config
from ..utils import FileOps, Colors, Logger
from ..utils.interactive_ui import InteractiveUI
from ..detectors import SeasonEpisodeDetector
from ..metadata import TMDBClient
from .media_processor import MediaProcessor


class SeriesProcessor(MediaProcessor):
    """Class for processing TV series files"""
    
    def __init__(self):
        """Initialize the processor"""
        super().__init__()
        # Initialize TMDB client if enabled
        self.tmdb_client = TMDBClient(interactive=Config.INTERACTIVE_MODE) if Config.TMDB_ENABLED else None
        # Keep a cache of series TMDB IDs to avoid repeated lookups
        self.series_tmdb_cache = {}
    
    def get_tmdb_id(self, title, year=None, filename=None):
        """
        Get TMDB ID for a TV series
        
        Args:
            title (str): Series title
            year (str, optional): First air year
            filename (str, optional): Original filename for interactive mode
            
        Returns:
            tuple: (tmdb_id, year) if found, (None, original_year) otherwise
        """
        if not self.tmdb_client or not Config.TMDB_ENABLED:
            return None, year
        
        # Check cache first
        cache_key = f"{title}_{year if year else ''}"
        if cache_key in self.series_tmdb_cache:
            return self.series_tmdb_cache[cache_key]
            
        tv_show = self.tmdb_client.search_tv(title, year, filename)
        
        # Check if user skipped
        if tv_show is None and Config.INTERACTIVE_MODE:
            return None, None
            
        if tv_show:
            tmdb_id = tv_show.get('id')
            # Get year from TMDB if not provided
            if not year and 'first_air_date' in tv_show and tv_show['first_air_date']:
                year = tv_show['first_air_date'][:4]
                
            Logger.info(f"Found TMDB match for series '{title}': ID {tmdb_id}, Year: {year}")
            
            # Store in cache
            self.series_tmdb_cache[cache_key] = (tmdb_id, year)
            return tmdb_id, year
            
        Logger.warning(f"No TMDB match found for series: {title} {year if year else ''}")
        
        # Store negative result in cache
        self.series_tmdb_cache[cache_key] = (None, year)
        return None, year
    
    def process(self, file_path):
        """Process a TV series file"""
        filename = os.path.basename(file_path)
        
        # Display processing header
        action = "Testing (no changes)" if Config.TEST_MODE else "Moving and renaming"
        InteractiveUI.display_processing_header(filename, "TV show", action)
        
        Logger.info(f"Processing TV show: {filename}")
        
        # Clean name and detect season/episode
        clean_title = self.get_clean_title(filename)
        season_episode = SeasonEpisodeDetector.detect(filename)
        
        if not season_episode:
            print(f"{Colors.RED}⚠️ Could not detect series pattern for:{Colors.NC} {filename}")
            Logger.error(f"Could not detect series pattern for: {filename}")
            return False
        
        season_num, episode_num = season_episode
        
        # Extract series name (before the SxxExx pattern)
        series_name = re.sub(r'S[0-9]{1,2}E[0-9]{1,2}.*$', '', clean_title).strip()
        year, quality = self.get_year_and_quality(filename)
        
        # Try to get TMDB ID and possibly more accurate year
        tmdb_id_info = (None, year)
        if Config.TMDB_ENABLED:
            print(f"{Colors.BLUE}Searching TMDB for series:{Colors.NC} {series_name}")
            tmdb_id_info = self.get_tmdb_id(series_name, year, filename)
        
        # If user skipped in interactive mode, don't process the file
        if tmdb_id_info is None and Config.INTERACTIVE_MODE:
            print(f"{Colors.YELLOW}Skipped by user. File will not be processed.{Colors.NC}")
            return False
            
        tmdb_id, year = tmdb_id_info if tmdb_id_info else (None, year)
        
        # Special check for series named with year-like numbers (like "1923")
        if series_name == year:
            # If series name is the same as detected year, don't use the year suffix
            year = ""
        
        # Remove year from series name if included
        if year and year in series_name:
            series_name = re.sub(r'\s+' + re.escape(year), '', series_name).strip()
        
        # Format season number with leading zeros
        season_num = f"{int(season_num):02d}"
        
        # Add quality suffix if it exists
        quality_suffix = f" - {quality}" if quality else ""
        
        # Create series name with TMDB ID if available
        if tmdb_id:
            if year:
                series_dir_name = f"{series_name} ({year}) [tmdbid-{tmdb_id}]"
            else:
                series_dir_name = f"{series_name} [tmdbid-{tmdb_id}]"
        else:
            if year:
                series_dir_name = f"{series_name} ({year})"
            else:
                series_dir_name = series_name
        
        # Create series and season directories
        series_dir = os.path.join(Config.SERIES, series_dir_name)
        season_dir = os.path.join(series_dir, f"Season {season_num}")
        
        # Format episode name (keep original extension)
        extension = os.path.splitext(filename)[1]
        new_filename = f"{series_name} S{season_num}E{episode_num}{quality_suffix}{extension}"
        
        # Display what we're going to do
        destination = os.path.join(season_dir, new_filename)
        print(f"{Colors.GREEN}Series identified:{Colors.NC} {series_name} {f'({year})' if year else ''}")
        if tmdb_id:
            print(f"{Colors.GREEN}TMDB ID:{Colors.NC} {tmdb_id}")
        print(f"{Colors.GREEN}Season/Episode:{Colors.NC} S{season_num}E{episode_num}")
        print(f"{Colors.GREEN}New location:{Colors.NC} {destination}")
        
        # Move file
        result = FileOps.move_file(file_path, destination)
        
        # Display result
        InteractiveUI.display_result(
            success=result,
            message="TV episode processed successfully" if result else "Failed to process TV episode",
            original_path=file_path,
            destination_path=destination
        )
        
        return result