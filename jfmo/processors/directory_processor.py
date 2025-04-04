#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Directory processor for JFMO
"""

import os
import re
from ..config import Config
from ..utils import FileOps, Colors, Logger, Transliterator
from ..utils.output_formatter import OutputFormatter
from ..utils.interactive_ui import InteractiveUI
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
    
    def extract_series_info_from_directory(self, dir_name):
        """
        Extract series name, season, and quality from directory name
        
        Args:
            dir_name (str): Directory name
            
        Returns:
            tuple: (series_name, season_num, quality)
        """
        # Clean the directory name first
        clean_dir = FileOps.clean_name(dir_name)
        
        # Try to extract season number
        season_num = SeasonEpisodeDetector.detect_season_only(dir_name)
        
        # Try to extract quality
        quality_match = re.search(r'([0-9]{3,4})[pр]', dir_name)
        quality = f"[{quality_match.group(1)}p]" if quality_match else ""
        
        # Extract series name - remove season part if found
        series_name = clean_dir
        if season_num:
            # Remove season identifier (e.g., "s01", "season 1") from series name
            series_name = re.sub(r'\bs[0-9]{1,2}\b', '', series_name, flags=re.IGNORECASE).strip()
            series_name = re.sub(r'\bseason\s*[0-9]{1,2}\b', '', series_name, flags=re.IGNORECASE).strip()
        
        # Remove quality from series name
        if quality:
            series_name = re.sub(r'\b[0-9]{3,4}[pр]\b', '', series_name, flags=re.IGNORECASE).strip()
            
        # Clean up double spaces
        series_name = re.sub(r'\s+', ' ', series_name).strip()
        
        return series_name, season_num, quality
    
    def process_special_case(self, dir_path):
        """Process a special case directory"""
        dir_name = os.path.basename(dir_path)
        
        Logger.info(f"Processing special directory: {dir_name}")
        
        match = re.search(r'(La Casa de Papel) ([0-9])', dir_name)
        if not match:
            OutputFormatter.print_file_processing_result(
                success=False,
                message="Failed to process special case directory - pattern not recognized"
            )
            return False
            
        series_name = match.group(1)
        season_num = match.group(2)
        
        # Try to get TMDB ID
        tmdb_id_info = (None, None)
        if Config.TMDB_ENABLED:
            OutputFormatter.print_file_processing_info("TMDB Search", series_name)
            tmdb_id_info = self.series_processor.get_tmdb_id(series_name, None, dir_name)
        
        # If user skipped in interactive mode, don't process the directory
        if tmdb_id_info is None and Config.INTERACTIVE_MODE:
            OutputFormatter.print_file_processing_result(
                success=False,
                message="Skipped by user. Directory will not be processed."
            )
            return False
            
        tmdb_id, year = tmdb_id_info if tmdb_id_info else (None, None)
        
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
        
        OutputFormatter.print_file_processing_info("Special Series", series_name)
        OutputFormatter.print_file_processing_info("Season", season_num)
        if quality:
            OutputFormatter.print_file_processing_info("Quality", quality)
        OutputFormatter.print_file_processing_info("Target Directory", season_dir)
        
        Logger.info(f"Special series detected: {dir_name}")
        
        # Find files in directory
        episodes_processed = 0
        episodes_count = 0
        
        # First count episodes for progress information
        for root, _, files in os.walk(dir_path):
            for file in files:
                if FileOps.is_video_file(file):
                    episodes_count += 1
        
        # Process episodes
        for root, _, files in os.walk(dir_path):
            for file in files:
                if FileOps.is_video_file(file):
                    episode_path = os.path.join(root, file)
                    filename = os.path.basename(episode_path)
                    
                    OutputFormatter.print_file_processing_header(filename)
                    
                    episode_num = "01"  # Assume episode 1 by default
                    
                    # Try to extract episode number if it exists in the name
                    ep_match = re.search(r'E([0-9]{2})', filename) or re.search(r'([0-9]{2})\.mkv', filename)
                    if ep_match:
                        episode_num = ep_match.group(1)
                        OutputFormatter.print_file_processing_info("Episode", episode_num)
                    
                    # Format final name
                    extension = os.path.splitext(filename)[1]
                    new_filename = f"{series_name} S{season_num}E{episode_num}{quality_suffix}{extension}"
                    destination = os.path.join(season_dir, new_filename)
                    
                    OutputFormatter.print_file_processing_info("New Filename", new_filename)
                    
                    # Move file
                    result = FileOps.move_file(episode_path, destination)
                    episodes_processed += 1 if result else 0
                    
                    # Display result
                    OutputFormatter.print_file_processing_result(
                        success=result,
                        message="Episode processed successfully" if result else "Failed to process episode",
                        details={
                            "From": episode_path,
                            "To": destination
                        }
                    )
        
        # After moving all files, remove empty directory if needed
        if episodes_processed > 0:
            if FileOps.remove_empty_dir(dir_path):
                OutputFormatter.print_file_processing_info("Directory", f"Removed empty directory: {dir_path}")
            
        # Summary for this directory
        OutputFormatter.print_file_processing_result(
            success=episodes_processed > 0,
            message=f"Directory processed: {episodes_processed}/{episodes_count} episodes"
        )
        
        return episodes_processed > 0
    
    def process_directory(self, dir_path):
        """Process a directory potentially containing TV series"""
        dir_name = os.path.basename(dir_path)
        
        Logger.info(f"Processing directory: {dir_name}")
        
        # Check if it's a special case (like La Casa de Papel)
        if self.is_special_case(dir_name):
            return self.process_special_case(dir_path)
        
        # Extract information from directory name
        series_name, dir_season_num, dir_quality = self.extract_series_info_from_directory(dir_name)
        
        # General cleaning for other cases
        clean_series = series_name
        year = YearDetector.get_year(dir_name)
        
        # Try to transliterate
        original_name = clean_series
        clean_series = Transliterator.transliterate_text(clean_series)
        if original_name != clean_series:
            OutputFormatter.print_file_processing_info("Transliteration", f"{original_name} → {clean_series}")
        
        # Try to get TMDB ID
        tmdb_id_info = (None, year)
        if Config.TMDB_ENABLED:
            OutputFormatter.print_file_processing_info("TMDB Search", clean_series)
            tmdb_id_info = self.series_processor.get_tmdb_id(clean_series, year, dir_name)
        
        # If user skipped in interactive mode, don't process the directory
        if tmdb_id_info is None and Config.INTERACTIVE_MODE:
            OutputFormatter.print_file_processing_result(
                success=False,
                message="Skipped by user. Directory will not be processed."
            )
            return False
            
        tmdb_id, year = tmdb_id_info if tmdb_id_info else (None, year)
        
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
        
        OutputFormatter.print_file_processing_info("Series", clean_series)
        if year:
            OutputFormatter.print_file_processing_info("Year", year)
        if dir_season_num:
            OutputFormatter.print_file_processing_info("Directory Season", dir_season_num)
        if dir_quality:
            OutputFormatter.print_file_processing_info("Directory Quality", dir_quality)
        if tmdb_id:
            OutputFormatter.print_file_processing_info("TMDB ID", tmdb_id)
        OutputFormatter.print_file_processing_info("Target Directory", series_dir)
        
        # Find all episode files in the directory
        episodes_processed = 0
        episodes_count = 0
        
        # First count episodes for progress information
        for root, _, files in os.walk(dir_path):
            for file in files:
                if FileOps.is_video_file(file):
                    episodes_count += 1
        
        # Process episodes
        for root, _, files in os.walk(dir_path):
            for file in files:
                if FileOps.is_video_file(file):
                    episode_path = os.path.join(root, file)
                    filename = os.path.basename(episode_path)
                    
                    OutputFormatter.print_file_processing_header(filename)
                    
                    # Detect season and episode with multiple patterns
                    season_episode = SeasonEpisodeDetector.detect(filename)
                    
                    # If full pattern not found but we have season from directory
                    if not season_episode and dir_season_num:
                        # Try to extract just the episode number
                        episode_num = SeasonEpisodeDetector.detect_episode_only(filename)
                        if episode_num:
                            season_episode = (dir_season_num, episode_num)
                            OutputFormatter.print_file_processing_info("Detection", 
                                           f"Using season {dir_season_num} from directory")
                    
                    if season_episode:
                        season_num, episode_num = season_episode
                        
                        # Format season number with leading zeros
                        season_num = f"{int(season_num):02d}"
                        
                        # Get quality if it exists
                        file_quality = QualityDetector.get_quality(filename)
                        # Use directory quality if file doesn't have quality info
                        quality = file_quality if file_quality else dir_quality
                        quality_suffix = f" - {quality}" if quality else ""
                        
                        # Create season directory
                        season_dir = os.path.join(series_dir, f"Season {season_num}")
                        
                        OutputFormatter.print_file_processing_info("Season/Episode", f"S{season_num}E{episode_num}")
                        if quality:
                            OutputFormatter.print_file_processing_info("Quality", quality)
                        
                        # Format episode name
                        extension = os.path.splitext(filename)[1]
                        new_filename = f"{clean_series} S{season_num}E{episode_num}{quality_suffix}{extension}"
                        destination = os.path.join(season_dir, new_filename)
                        
                        OutputFormatter.print_file_processing_info("New Filename", new_filename)
                        
                        # Move file
                        result = FileOps.move_file(episode_path, destination)
                        episodes_processed += 1 if result else 0
                        
                        # Display result
                        OutputFormatter.print_file_processing_result(
                            success=result,
                            message="Episode processed successfully" if result else "Failed to process episode",
                            details={
                                "From": episode_path,
                                "To": destination
                            }
                        )
                    else:
                        error_message = f"Could not detect episode pattern for: {filename}"
                        Logger.error(error_message)
                        OutputFormatter.print_file_processing_result(
                            success=False,
                            message=error_message
                        )
        
        # After moving all files, remove empty directory if needed
        if episodes_processed > 0:
            if FileOps.remove_empty_dir(dir_path):
                OutputFormatter.print_file_processing_info("Directory", f"Removed empty directory: {dir_path}")
        
        # Summary for this directory
        OutputFormatter.print_file_processing_result(
            success=episodes_processed > 0,
            message=f"Directory processed: {episodes_processed}/{episodes_count} episodes"
        )
        
        return episodes_processed > 0