#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main module for JFMO
"""

import os
import sys
from .config import Config
from .utils import Colors, Logger, FileOps
from .detectors import SeasonEpisodeDetector
from .processors import MovieProcessor, SeriesProcessor, DirectoryProcessor
from .cli import parse_args, check_root, check_dependencies, handle_config_options, update_config_from_args


def print_header():
    """Print JFMO header information"""
    print(f"{Colors.GREEN}🎬 JELLYFIN FORMAT MEDIA ORGANIZER{Colors.NC}")
    
    if Config.TEST_MODE:
        print(f"{Colors.YELLOW}MODE: TEST{Colors.NC} - No actual file operations will be performed")
    else:
        print(f"{Colors.YELLOW}MODE: MOVE{Colors.NC} - Files will be moved to their destinations and empty directories will be removed")
    
    print("")
    print(f"{Colors.BLUE}📂 Downloads directory:{Colors.NC} {Config.DOWNLOADS}")
    print(f"{Colors.BLUE}🎥 Movies directory:{Colors.NC} {Config.FILMS}")
    print(f"{Colors.BLUE}📺 TV Shows directory:{Colors.NC} {Config.SERIES}")
    print(f"{Colors.BLUE}👤 Media ownership:{Colors.NC} {Config.MEDIA_USER}:{Config.MEDIA_GROUP}")
    print(f"{Colors.BLUE}🔤 Automatic transliteration:{Colors.NC} Enabled")
    
    if Config.TMDB_ENABLED:
        api_status = "Configured ✓" if Config.TMDB_API_KEY else "Not configured ✗"
        print(f"{Colors.BLUE}🎬 TMDB Integration:{Colors.NC} Enabled ({api_status})")
    else:
        print(f"{Colors.BLUE}🎬 TMDB Integration:{Colors.NC} Disabled")
        
    print(f"{Colors.BLUE}📄 Log file:{Colors.NC} {Config.LOG_FILE}")
    print("")


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


def process_files():
    """Process individual media files"""
    Logger.info("Starting processing of individual files")
    print(f"{Colors.GREEN}=== PROCESSING INDIVIDUAL FILES ==={Colors.NC}")
    print("")
    
    movie_processor = MovieProcessor()
    series_processor = SeriesProcessor()
    
    # Process individual files (look for series first)
    for filename in os.listdir(Config.DOWNLOADS):
        file_path = os.path.join(Config.DOWNLOADS, filename)
        if os.path.isfile(file_path) and FileOps.is_video_file(filename):
            # Check if it's a series episode (SxxExx pattern)
            if SeasonEpisodeDetector.detect(filename):
                series_processor.process(file_path)
            else:
                # If not a series, treat as movie
                movie_processor.process(file_path)


def process_directories():
    """Process directories potentially containing series"""
    Logger.info("Starting directory processing")
    print(f"{Colors.GREEN}=== PROCESSING SERIES DIRECTORIES ==={Colors.NC}")
    print("")
    
    directory_processor = DirectoryProcessor()
    
    # Process directories (series)
    for dirname in os.listdir(Config.DOWNLOADS):
        dir_path = os.path.join(Config.DOWNLOADS, dirname)
        if os.path.isdir(dir_path) and dirname != "incomplete":
            directory_processor.process_directory(dir_path)


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
    print_header()
    
    # Check directories
    check_directories()
    
    # Process files
    process_files()
    
    # Process directories
    process_directories()
    
    # Final message
    print("")
    print(f"{Colors.GREEN}✅ PROCESS COMPLETED{Colors.NC}")
    print(f"{Colors.BLUE}A detailed log has been saved at: {Config.LOG_FILE}{Colors.NC}")


if __name__ == "__main__":
    main()