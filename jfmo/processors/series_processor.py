import os
import re
from ..config import Config
from ..utils import Logger, Transliterator, TMDBCache, FilenameFormatter
from ..utils.output_formatter import OutputFormatter
from ..detectors import SeasonEpisodeDetector
from ..metadata import TMDBClient
from .media_processor import MediaProcessor


class SeriesProcessor(MediaProcessor):
    """Class for processing TV series files"""
    
    def __init__(self):
        """Initialize the processor"""
        super().__init__()
        self.tmdb_client = TMDBClient(interactive=Config.INTERACTIVE_MODE) if Config.TMDB_ENABLED else None
        self.tmdb_cache = TMDBCache()
    
    def get_tmdb_id(self, title, year=None, filename=None):
        """
        Get TMDB ID for a TV series with caching
        
        Args:
            title: Series title
            year: First air year
            filename: Original filename for interactive mode
            
        Returns:
            tuple: (tmdb_id, year) if found, (None, original_year) otherwise
        """
        if not self.tmdb_client or not Config.TMDB_ENABLED:
            return None, year
        
        # Check cache first
        cached = self.tmdb_cache.get(title, year)
        if cached is not None:
            if cached[0]:
                OutputFormatter.print_file_processing_info("TMDB", f"Using cached ID: {cached[0]}")
            return cached
        
        # Search TMDB
        OutputFormatter.print_file_processing_info("TMDB Search", title)
        tv_show = self.tmdb_client.search_tv(title, year, filename)
        
        # Check if user skipped
        if tv_show is None and Config.INTERACTIVE_MODE:
            return None, None
            
        if tv_show:
            tmdb_id = tv_show.get('id')
            
            # Get year from TMDB if available
            if 'first_air_date' in tv_show and tv_show['first_air_date']:
                tmdb_year = tv_show['first_air_date'][:4]
                if tmdb_year:
                    year = tmdb_year
                
            Logger.info(f"Found TMDB match for series '{title}': ID {tmdb_id}, Year: {year}")
            OutputFormatter.print_file_processing_info("TMDB Match", f"ID: {tmdb_id}, Year: {year}")
            
            # Cache result
            self.tmdb_cache.set(title, year, tmdb_id, year)
            return tmdb_id, year
            
        Logger.warning(f"No TMDB match found for series: {title} {year if year else ''}")
        OutputFormatter.print_file_processing_info("TMDB", "No match found")
        
        # Cache negative result
        self.tmdb_cache.set(title, year, None, year)
        return None, year
        
    def process(self, file_path):
        """Process a TV series file"""
        filename = os.path.basename(file_path)
        extension = os.path.splitext(filename)[1]
        
        Logger.info(f"Processing TV show: {filename}")
        
        # Detect season/episode
        season_episode = SeasonEpisodeDetector.detect(filename)
        
        if not season_episode:
            error_message = f"Could not detect series pattern for: {filename}"
            Logger.error(error_message)
            OutputFormatter.print_file_processing_result(
                success=False,
                message=error_message
            )
            return False
        
        season_num, episode_num = season_episode
        
        # Handle numeric series names (like 1923)
        numeric_series_match = re.match(r'^([12][0-9]{3})\.', filename)
        numeric_series_name = numeric_series_match.group(1) if numeric_series_match else None
        
        if numeric_series_name:
            OutputFormatter.print_file_processing_info("Detected Numeric Series", numeric_series_name)
        
        # Get clean title
        clean_title = self.get_clean_title(filename)
        
        if numeric_series_name and not clean_title.strip():
            clean_title = numeric_series_name
        
        # Remove S01.E01 pattern that might remain
        if re.search(r'S[0-9]{1,2}\s*\.\s*E[0-9]{1,2}', clean_title, re.IGNORECASE):
            clean_title = re.sub(r'S[0-9]{1,2}\s*\.\s*E[0-9]{1,2}.*', '', clean_title, re.IGNORECASE).strip()
        
        series_name = clean_title
        
        if not series_name.strip() and numeric_series_name:
            series_name = numeric_series_name
        else:
            # Remove years from title
            series_name = re.sub(r'\b(19|20)[0-9]{2}\b', '', series_name).strip()
        
        OutputFormatter.print_file_processing_info("Series", series_name)
        OutputFormatter.print_file_processing_info("Season/Episode", f"S{int(season_num):02d}E{episode_num}")
        
        # Transliterate before getting metadata
        original_name = series_name
        series_name = Transliterator.transliterate_text(series_name)
        if original_name != series_name:
            OutputFormatter.print_file_processing_info("Transliteration", f"{original_name} → {series_name}")
        
        # Get year and quality
        year, quality = self.get_year_and_quality(filename)
        
        if year:
            OutputFormatter.print_file_processing_info("Year", year)
        if quality:
            OutputFormatter.print_file_processing_info("Quality", quality)
        
        # Get TMDB ID
        tmdb_id_info = (None, year)
        if Config.TMDB_ENABLED:
            tmdb_id_info = self.get_tmdb_id(series_name, year, filename)
        
        # Check if user skipped
        if tmdb_id_info is None and Config.INTERACTIVE_MODE:
            OutputFormatter.print_file_processing_result(
                success=False,
                message="Skipped by user. File will not be processed."
            )
            return False
        
        tmdb_id, year = tmdb_id_info if tmdb_id_info else (None, year)
        
        # Special check: don't use year if it's the series name (like "1923")
        if numeric_series_name and series_name == numeric_series_name:
            if year == series_name:
                year = None
        
        # Format season number
        season_num = f"{int(season_num):02d}"
        
        # Format directory and filename using shared formatters
        series_dir_name = FilenameFormatter.format_series_directory(
            series_name=series_name,
            year=year,
            tmdb_id=tmdb_id
        )
        
        new_filename = FilenameFormatter.format_series_filename(
            series_name=series_name,
            season=season_num,
            episode=episode_num,
            quality=quality,
            extension=extension
        )
        
        # Create paths
        series_dir = os.path.join(Config.SERIES, series_dir_name)
        season_dir = os.path.join(series_dir, f"Season {season_num}")
        destination = os.path.join(season_dir, new_filename)
        
        OutputFormatter.print_file_processing_info("Series Directory", series_dir_name)
        OutputFormatter.print_file_processing_info("New Filename", new_filename)
        OutputFormatter.print_file_processing_info("Destination", destination)
        
        # Move file
        from ..utils import FileOps
        result = FileOps.move_file(file_path, destination)
        
        OutputFormatter.print_file_processing_result(
            success=result,
            message="TV episode processed successfully" if result else "Failed to process TV episode",
            details={
                "From": file_path,
                "To": destination
            }
        )
        
        return result