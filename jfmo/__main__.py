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
            
            # Verificación de patrones más estricta para series
            is_series = False
            
            # Primero verificar patrones definitivos de series
            # Patrón SxxExx o S01.E01 o NxNN
            if re.search(r'S[0-9]{1,2}\.?E[0-9]{1,2}', filename, re.IGNORECASE) or \
               re.search(r'[0-9]{1,2}x[0-9]{1,2}', filename, re.IGNORECASE):
                is_series = True
            
            # Patrones que podrían ser confusos
            elif re.search(r'Episode\s*[0-9]{1,2}', filename, re.IGNORECASE):
                # Para "Episode N", solo tratar como serie si menciona un show conocido
                is_series = any(series in filename for series in [
                    'Loki', 'Mandalorian', 'Walking Dead', 'Doctor Who', 'Game of Thrones'
                ])
            
            # Excluir patrones específicos de películas
            # Películas conocidas
            known_movies = ['2001', 'Interstellar', 'Ocean', 'Matrix', 'Avatar', 'Inception',
                          'Pulp Fiction', 'Dune', 'Oppenheimer']
            is_known_movie = any(movie.lower() in filename.lower() for movie in known_movies)
            
            # Si es un número de 4 dígitos al inicio, tratar como serie (como 1923, 1883)
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
                    # Si parece serie pero no se pudo detectar patrón, tratar como película
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