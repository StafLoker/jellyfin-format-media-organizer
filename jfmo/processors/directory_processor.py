#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Directory processor for JFMO
"""

import os
import re
from ..config import Config
from ..utils import FileOps, Colors, Logger, Transliterator
from ..detectors import SeasonEpisodeDetector, YearDetector, QualityDetector
from ..metadata import TMDBClient
from .series_processor import SeriesProcessor


class DirectoryProcessor:
    """Class for processing directories containing TV series"""
    
    def __init__(self):
        """Initialize the processor"""
        self.series_processor = SeriesProcessor()
        # Use the same TMDB client as the series processor
        self.tmdb_client = self.series_processor.tmdb_client
    
    def is_special_case(self, dir_name):
        """Check if directory is a special case (like "La Casa de Papel 3")"""
        return bool(re.search(r'(La Casa de Papel) ([0-9])', dir_name))
    
    def process_special_case(self, dir_path):
        """Process a special case directory"""
        dir_name = os.path.basename(dir_path)
        Logger.info(f"Processing special directory: {dir_name}")
        
        match = re.search(r'(La Casa de Papel) ([0-9])', dir_name)
        if not match:
            return False
            
        series_name = match.group(1)
        season_num = match.group(2)
        
        # Try to get TMDB ID
        tmdb_id_info = (None, None)
        if Config.TMDB_ENABLED:
            print(f"{Colors.BLUE}Searching TMDB for series:{Colors.NC} {series_name}")
            tmdb_id_info = self.series_processor.get_tmdb_id(series_name)
        
        tmdb_id, year = tmdb_id_info
        
        # Format season
        season_num = f"{int(season_num):02d}"
        
        # Get quality if it exists
        quality = ""
        quality_suffix = ""
        quality_match = re.search(r'\[([0-9]+p)\]', dir_name)
        if quality_match:
            quality = f"[{quality_match.group(1)}]"
            quality_suffix = f" - {quality}"
        
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
        
        # Create structure
        series_dir = os.path.join(Config.SERIES, series_dir_name)
        season_dir = os.path.join(series_dir, f"Season {season_num}")
        
        print(f"{Colors.BLUE}Special series detected:{Colors.NC} {dir_name}")
        Logger.info(f"Special series detected: {dir_name}")
        
        # Find files in directory
        for root, _, files in os.walk(dir_path):
            for file in files:
                if FileOps.is_video_file(file):
                    episode_path = os.path.join(root, file)
                    filename = os.path.basename(episode_path)
                    episode_num = "01"  # Assume episode 1 by default
                    
                    # Try to extract episode number if it exists in the name
                    ep_match = re.search(r'E([0-9]{2})', filename) or re.search(r'([0-9]{2})\.mkv', filename)
                    if ep_match:
                        episode_num = ep_match.group(1)
                    
                    # Format final name
                    extension = os.path.splitext(filename)[1]
                    new_filename = f"{series_name} S{season_num}E{episode_num}{quality_suffix}{extension}"
                    
                    # Move file
                    FileOps.move_file(episode_path, os.path.join(season_dir, new_filename))
        
        # After moving all files, remove empty directory
        FileOps.remove_empty_dir(dir_path)
        
        return True
    
    def process_directory(self, dir_path):
        """Process a directory potentially containing TV series"""
        dir_name = os.path.basename(dir_path)
        Logger.info(f"Processing directory: {dir_name}")
        
        # Check if it's a special case (like La Casa de Papel)
        if self.is_special_case(dir_name):
            return self.process_special_case(dir_path)
        
        # General cleaning for other cases
        clean_series = FileOps.clean_name(dir_name)
        year = YearDetector.get_year(dir_name)
        
        # Try to transliterate
        clean_series = Transliterator.transliterate_text(clean_series)
        
        # Try to get TMDB ID
        tmdb_id_info = (None, year)
        if Config.TMDB_ENABLED:
            print(f"{Colors.BLUE}Searching TMDB for series:{Colors.NC} {clean_series}")
            tmdb_id_info = self.series_processor.get_tmdb_id(clean_series, year)
        
        tmdb_id, year = tmdb_id_info
        
        # Special check for series named with year-like numbers (like "1923")
        if clean_series == year:
            # If series name is the same as detected year, don't use the year suffix
            year = ""
        
        # Remove year from name if included
        if year and year in clean_series:
            clean_series = re.sub(r'\s+' + re.escape(year), '', clean_series).strip()
        
        # Create series name with TMDB ID if available
        if tmdb_id:
            if year:
                series_dir_name = f"{clean_series} ({year}) [tmdbid-{tmdb_id}]"
            else:
                series_dir_name = f"{clean_series} [tmdbid-{tmdb_id}]"
        else:
            if year:
                series_dir_name = f"{clean_series} ({year})"
            else:
                series_dir_name = clean_series
        
        # Create series directory
        series_dir = os.path.join(Config.SERIES, series_dir_name)
        
        print(f"{Colors.BLUE}Processing series directory:{Colors.NC} {dir_name}")
        
        # Find all episode files in the directory
        for root, _, files in os.walk(dir_path):
            for file in files:
                if FileOps.is_video_file(file):
                    episode_path = os.path.join(root, file)
                    filename = os.path.basename(episode_path)
                    
                    # Detect season and episode with multiple patterns
                    season_episode = SeasonEpisodeDetector.detect(filename)
                    if season_episode:
                        season_num, episode_num = season_episode
                        
                        # Format season number with leading zeros
                        season_num = f"{int(season_num):02d}"
                        
                        # Get quality if it exists
                        quality = QualityDetector.get_quality(filename)
                        quality_suffix = f" - {quality}" if quality else ""
                        
                        # Create season directory
                        season_dir = os.path.join(series_dir, f"Season {season_num}")
                        
                        # Format episode name
                        extension = os.path.splitext(filename)[1]
                        new_filename = f"{clean_series} S{season_num}E{episode_num}{quality_suffix}{extension}"
                        
                        # Move file
                        FileOps.move_file(episode_path, os.path.join(season_dir, new_filename))
                    else:
                        print(f"{Colors.RED}⚠️ Could not detect episode pattern for:{Colors.NC} {filename}")
                        Logger.error(f"Could not detect episode pattern for: {filename}")
        
        # After moving all files, remove empty directory
        FileOps.remove_empty_dir(dir_path)
        
        return True