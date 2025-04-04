#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Series processor for JFMO
"""

import os
import re
from ..config import Config
from ..utils import FileOps, Colors, Logger
from ..detectors import SeasonEpisodeDetector
from .media_processor import MediaProcessor


class SeriesProcessor(MediaProcessor):
    """Class for processing TV series files"""
    
    def process(self, file_path):
        """Process a TV series file"""
        filename = os.path.basename(file_path)
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
        
        # Special check for series named with year-like numbers (like "1923")
        if series_name == year:
            # If series name is the same as detected year, don't use the year suffix
            year = ""
        
        year_suffix = ""
        if year:
            year_suffix = f" ({year})"
            # Remove year from series name if included
            series_name = series_name.replace(f" {year}", "")
        
        # Format season number with leading zeros
        season_num = f"{int(season_num):02d}"
        
        # Add quality suffix if it exists
        quality_suffix = f" - {quality}" if quality else ""
        
        # Create series and season directories
        series_dir = os.path.join(Config.SERIES, f"{series_name}{year_suffix}")
        season_dir = os.path.join(series_dir, f"Season {season_num}")
        
        # Format episode name (keep original extension)
        extension = os.path.splitext(filename)[1]
        new_filename = f"{series_name} S{season_num}E{episode_num}{quality_suffix}{extension}"
        
        # Move file
        return FileOps.move_file(file_path, os.path.join(season_dir, new_filename))
