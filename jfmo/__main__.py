#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main module for JFMO
"""

import os
import sys
import re
from collections import defaultdict

from .config import Config
from .utils import Colors, Logger, FileOps
from .utils.output_formatter import OutputFormatter
from .detectors import SeasonEpisodeDetector
from .processors import MovieProcessor, SeriesProcessor, DirectoryProcessor
from .cli import parse_args, check_root, check_dependencies, handle_config_options, update_config_from_args


def should_skip_file(filename):
    """
    Check if a file should be skipped based on suspicious patterns
    
    Args:
        filename (str): The filename to check
        
    Returns:
        tuple: (should_skip, reason) whether to skip and why
    """
    # Standard series patterns that should NOT be skipped
    standard_series_patterns = [
        # Standard SxxExx pattern - these should be processed normally as series
        r'S[0-9]{1,2}E[0-9]{1,2}',
        # Dotted pattern S01.E01
        r'S[0-9]{1,2}\.E[0-9]{1,2}',
        # Lowercase sXXeXX pattern
        r'\bs[0-9]{1,2}e[0-9]{1,2}\b',
        # Multi-episode format (now allowed)
        r'S[0-9]{1,2}E[0-9]{1,2}-E?[0-9]{1,2}',
        # Season x Episode format (now allowed)
        r'[0-9]{1,2}[xX][0-9]{1,2}'
    ]
    
    # If it matches a standard series pattern, don't skip it
    for pattern in standard_series_patterns:
        if re.search(pattern, filename, re.IGNORECASE):
            return False, ""
    
    # Suspicious patterns that should be skipped
    suspicious_patterns = [
        # Shows with episode markers but might be missed by standard detectors
        (r'[Ee]pisode[. ]([0-9]{1,2})', "Contains 'Episode X' pattern"),
        (r'\b([0-9]{1})([0-9]{2})\b', "Potential season/episode number (NNN format)"),
        # Date-based TV shows
        (r'(19|20)[0-9]{2}[.-][0-9]{2}[.-][0-9]{2}', "Date-based TV show format"),
        # Non-standard episode numbering in Russian content
        (r'[Ee][0-9]{2}.*[0-9]{4}', "Non-standard episode numbering")
    ]
    
    # Check if any suspicious pattern is found
    for pattern, reason in suspicious_patterns:
        if re.search(pattern, filename, re.IGNORECASE):
            # Check for specific exceptions (valid movies with similar patterns)
            if pattern == r'\b([0-9]{1})([0-9]{2})\b':
                # Don't skip if it's a movie with a year and quality pattern
                if re.search(r'(19|20)[0-9]{2}.*\b(720|1080|2160)p\b', filename, re.IGNORECASE):
                    continue
            
            return True, reason
    
    return False, ""

def process_files():
    """Process individual media files"""
    Logger.info("Starting processing of individual files")
    OutputFormatter.print_section_header("PROCESSING INDIVIDUAL FILES")
    
    movie_processor = MovieProcessor()
    series_processor = SeriesProcessor()
    
    stats = defaultdict(int)
    
    # Process individual files
    for filename in os.listdir(Config.DOWNLOADS):
        file_path = os.path.join(Config.DOWNLOADS, filename)
        if os.path.isfile(file_path) and FileOps.is_video_file(filename):
            stats['total'] += 1
            
            OutputFormatter.print_file_processing_header(filename)
            
            # Check if file should be skipped due to ambiguous patterns
            should_skip, skip_reason = should_skip_file(filename)
            if should_skip:
                OutputFormatter.print_file_processing_info("Action", "Skip")
                OutputFormatter.print_file_processing_info("Reason", f"Ambiguous pattern: {skip_reason}")
                OutputFormatter.print_file_processing_result(
                    success=True,
                    message="File skipped due to ambiguous pattern",
                    details={"File": file_path}
                )
                stats['skipped'] += 1
                continue
            
            # Process by standard patterns first - very strong indicators
            # Pattern SxxExx definitely indicates a TV series
            if re.search(r'S[0-9]{1,2}E[0-9]{1,2}', filename, re.IGNORECASE) or \
               re.search(r'S[0-9]{1,2}\.E[0-9]{1,2}', filename, re.IGNORECASE) or \
               re.search(r'\bs[0-9]{1,2}e[0-9]{1,2}\b', filename) or \
               re.search(r'S[0-9]{1,2}E[0-9]{1,2}-E?[0-9]{1,2}', filename, re.IGNORECASE) or \
               re.search(r'[0-9]{1,2}[xX][0-9]{1,2}', filename):
                OutputFormatter.print_file_processing_info("Detected", "TV Series")
                season_episode = SeasonEpisodeDetector.detect(filename)
                if season_episode:
                    OutputFormatter.print_file_processing_info("Season/Episode", 
                               f"S{int(season_episode[0]):02d}E{int(season_episode[1]):02d}")
                    
                    result = series_processor.process(file_path)
                    if result:
                        stats['success'] += 1
                    else:
                        stats['error'] += 1
                    continue
            
            # Stricter pattern verification for series
            is_series = False
            
            # First check definitive series patterns
            # SxxExx or S01.E01 or NxNN patterns
            if re.search(r'S[0-9]{1,2}\.?E[0-9]{1,2}', filename, re.IGNORECASE) or \
               re.search(r'[0-9]{1,2}x[0-9]{1,2}', filename, re.IGNORECASE) or \
               re.search(r'S[0-9]{1,2}E[0-9]{1,2}-E?[0-9]{1,2}', filename, re.IGNORECASE):
                is_series = True
            
            # Potentially confusing patterns
            elif re.search(r'Episode\s*[0-9]{1,2}', filename, re.IGNORECASE):
                # For "Episode N", only treat as series if it mentions a known show
                is_series = any(series in filename for series in [
                    'Loki', 'Mandalorian', 'Walking Dead', 'Doctor Who', 'Game of Thrones'
                ])
            
            # Detect using more robust patterns instead of a predefined list
            # Check if it looks like a typical movie (year followed by quality)
            movie_pattern = re.search(r'(19|20)[0-9]{2}.*\b(720p|1080p|2160p|HDR|BluRay)\b', filename, re.IGNORECASE)
            is_known_movie = bool(movie_pattern)
            
            # If it's a 4-digit number at the beginning, treat as series (like 1923, 1883)
            if re.match(r'^[12][0-9]{3}\.S[0-9]{1,2}', filename):
                is_series = True
                is_known_movie = False
            
            if is_known_movie:
                is_series = False
            
            if is_series:
                season_episode = SeasonEpisodeDetector.detect(filename)
                if season_episode:
                    OutputFormatter.print_file_processing_info("Detected", "TV Series")
                    OutputFormatter.print_file_processing_info("Season/Episode", 
                                   f"S{int(season_episode[0]):02d}E{int(season_episode[1]):02d}")
                    
                    result = series_processor.process(file_path)
                    if result:
                        stats['success'] += 1
                    else:
                        stats['error'] += 1
                else:
                    # If it looks like a series but pattern couldn't be detected, treat as movie
                    OutputFormatter.print_file_processing_info("Detected", "Movie (fallback from failed series detection)")
                    result = movie_processor.process(file_path)
                    if result:
                        stats['success'] += 1
                    else:
                        stats['error'] += 1
            else:
                OutputFormatter.print_file_processing_info("Detected", "Movie")
                
                result = movie_processor.process(file_path)
                if result:
                    stats['success'] += 1
                else:
                    stats['error'] += 1
    
    return stats


def process_directories():
    """Process directories potentially containing series"""
    Logger.info("Starting directory processing")
    OutputFormatter.print_section_header("PROCESSING SERIES DIRECTORIES")
    
    directory_processor = DirectoryProcessor()
    
    stats = defaultdict(int)
    
    # Process directories (series)
    for dirname in os.listdir(Config.DOWNLOADS):
        dir_path = os.path.join(Config.DOWNLOADS, dirname)
        if os.path.isdir(dir_path) and dirname != "incomplete":
            stats['total'] += 1
            
            # Check if it's a special case directory
            if directory_processor.is_special_case(dirname):
                action = "Testing (no changes)" if Config.TEST_MODE else "Moving and renaming"
                OutputFormatter.print_directory_header(dirname, "TV show directory (special case)", action)
                
                result = directory_processor.process_special_case(dir_path)
                if result:
                    stats['success'] += 1
                else:
                    stats['error'] += 1
            else:
                action = "Testing (no changes)" if Config.TEST_MODE else "Moving and renaming"
                OutputFormatter.print_directory_header(dirname, "TV show directory", action)
                
                result = directory_processor.process_directory(dir_path)
                if result:
                    stats['success'] += 1
                else:
                    stats['error'] += 1
    
    return stats


def check_directories():
    """Check if required directories exist and create them if needed"""
    # Verify that directories exist
    if not os.path.isdir(Config.DOWNLOADS):
        print(f"{Colors.RED}Error: Downloads directory does not exist{Colors.NC}")
        Logger.error(f"Downloads directory does not exist: {Config.DOWNLOADS}")
        sys.exit(1)
    
    # Make sure series and films directories exist with proper permissions
    FileOps.ensure_dir(Config.SERIES)
    FileOps.ensure_dir(Config.FILMS)


def main():
    """Main function of JFMO"""
    # Parse command line arguments
    args = parse_args()
    
    # Handle configuration file first
    handle_config_options(args)
    
    # Then update config from command line arguments (overriding config file)
    update_config_from_args(args)
    
    # Check if running as root
    check_root()
    
    # Check dependencies
    check_dependencies()
    
    # Print header
    OutputFormatter.print_header()
    
    # Check directories
    check_directories()
    
    # Initialize stats
    all_stats = defaultdict(int)
    
    # Process files
    file_stats = process_files()
    for key, value in file_stats.items():
        all_stats[key] += value
    
    # Process directories
    dir_stats = process_directories()
    for key, value in dir_stats.items():
        all_stats[key] += value
    
    # Print summary
    OutputFormatter.print_summary(all_stats)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())