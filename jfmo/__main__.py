import os
import sys
from collections import defaultdict

from .config import Config
from .utils import Colors, Logger, FileOps, IncompleteChecker
from .utils.output_formatter import OutputFormatter
from .detectors import SeasonEpisodeDetector, MediaTypeDetector
from .processors import MovieProcessor, SeriesProcessor, DirectoryProcessor
from .cli import parse_args, check_root, check_dependencies, handle_config_options, update_config_from_args
from .daemon import DaemonManager


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
        if not (os.path.isfile(file_path) and FileOps.is_video_file(filename)):
            continue
        
        stats['total'] += 1
        OutputFormatter.print_file_processing_header(filename)
        
        # Check for ambiguous patterns
        is_ambiguous, skip_reason = MediaTypeDetector.is_ambiguous(filename)
        if is_ambiguous:
            OutputFormatter.print_file_processing_info("Action", "Skip")
            OutputFormatter.print_file_processing_info("Reason", f"Ambiguous pattern: {skip_reason}")
            OutputFormatter.print_file_processing_result(
                success=None,
                message="File skipped due to ambiguous pattern",
                details={"File": file_path}
            )
            stats['skipped'] += 1
            continue
        
        # Determine if it's a series or movie
        if MediaTypeDetector.is_series(filename):
            # Process as series
            OutputFormatter.print_file_processing_info("Detected", "TV Series")
            season_episode = SeasonEpisodeDetector.detect(filename)
            
            if not season_episode:
                OutputFormatter.print_file_processing_result(
                    success=False,
                    message="Could not detect season/episode pattern"
                )
                stats['error'] += 1
                continue
            
            season_num, episode_num = season_episode
            OutputFormatter.print_file_processing_info("Season/Episode", 
                       f"S{int(season_num):02d}E{int(episode_num):02d}")
            
            # Check for incomplete episodes
            clean_title = FileOps.clean_name(filename)
            if IncompleteChecker.has_incomplete_episodes(clean_title, f"{int(season_num):02d}"):
                OutputFormatter.print_file_processing_result(
                    success=None,
                    message="Skipped - incomplete episodes exist in incomplete directory",
                    details={"File": file_path}
                )
                stats['skipped'] += 1
                continue
            
            result = series_processor.process(file_path)
        else:
            # Process as movie
            OutputFormatter.print_file_processing_info("Detected", "Movie")
            result = movie_processor.process(file_path)
        
        stats['success' if result else 'error'] += 1
    
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
        if not os.path.isdir(dir_path) or dirname == "incomplete":
            continue
        
        stats['total'] += 1
        
        # Check if it's a special case directory
        if directory_processor.is_special_case(dirname):
            action = "Testing (no changes)" if Config.TEST_MODE else "Moving and renaming"
            OutputFormatter.print_directory_header(dirname, "TV show directory (special case)", action)
            result = directory_processor.process_special_case(dir_path)
        else:
            action = "Testing (no changes)" if Config.TEST_MODE else "Moving and renaming"
            OutputFormatter.print_directory_header(dirname, "TV show directory", action)
            result = directory_processor.process_directory(dir_path)
        
        stats['success' if result else 'error'] += 1
    
    return stats


def check_directories():
    """Check if required directories exist and create them if needed"""
    if not os.path.isdir(Config.DOWNLOADS):
        print(f"{Colors.RED}Error: Downloads directory does not exist{Colors.NC}")
        Logger.error(f"Downloads directory does not exist: {Config.DOWNLOADS}")
        sys.exit(1)
    
    # Ensure series and films directories exist
    FileOps.ensure_dir(Config.SERIES)
    FileOps.ensure_dir(Config.FILMS)


def main():
    """Main function of JFMO"""
    # Parse command line arguments
    args = parse_args()
    
    # Handle configuration file first
    handle_config_options(args)
    
    # Update config from command line arguments (overriding config file)
    update_config_from_args(args)
    
    # Check if running as root (only in non-test, non-daemon mode)
    if not Config.DAEMON_MODE:
        check_root()
    
    # Check dependencies
    check_dependencies()
    
    # If daemon mode, start daemon and exit
    if Config.DAEMON_MODE:
        daemon = DaemonManager()
        return 0 if daemon.start(
            watch_dir=Config.DOWNLOADS,
            incomplete_dir=Config.INCOMPLETE_DIR,
            check_interval=Config.DAEMON_INTERVAL
        ) else 1
    
    # Normal mode - print header
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