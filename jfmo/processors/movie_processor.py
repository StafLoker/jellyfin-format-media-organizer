import os
import re
from ..config import Config
from ..utils import Logger, Transliterator, TMDBCache, FilenameFormatter
from ..utils.output_formatter import OutputFormatter
from ..metadata import TMDBClient
from .media_processor import MediaProcessor


class MovieProcessor(MediaProcessor):
    """Class for processing movie files"""
    
    def __init__(self):
        """Initialize the processor"""
        super().__init__()
        self.tmdb_client = TMDBClient(interactive=Config.INTERACTIVE_MODE) if Config.TMDB_ENABLED else None
        self.tmdb_cache = TMDBCache()
    
    def get_tmdb_id(self, title, year=None, filename=None):
        """
        Get TMDB ID for a movie with caching
        
        Args:
            title: Movie title
            year: Release year
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
        movie = self.tmdb_client.search_movie(title, year, filename)
        
        if movie:
            tmdb_id = movie.get('id')
            # Get year from TMDB if not provided or more accurate
            if 'release_date' in movie and movie['release_date']:
                year = movie['release_date'][:4]
                
            Logger.info(f"Found TMDB match for '{title}': ID {tmdb_id}, Year: {year}")
            OutputFormatter.print_file_processing_info("TMDB Match", f"ID: {tmdb_id}, Year: {year}")
            
            # Cache result
            self.tmdb_cache.set(title, year, tmdb_id, year)
            return tmdb_id, year
            
        Logger.warning(f"No TMDB match found for movie: {title} {year if year else ''}")
        OutputFormatter.print_file_processing_info("TMDB", "No match found")
        
        # Cache negative result
        self.tmdb_cache.set(title, year, None, year)
        return None, year
    
    def process(self, file_path):
        """Process a movie file"""
        filename = os.path.basename(file_path)
        extension = os.path.splitext(filename)[1]
        
        Logger.info(f"Processing movie: {filename}")
        
        # Handle numeric movie names (like 2001.A.Space.Odyssey)
        numeric_movie_match = re.match(r'^([12][0-9]{3})\.', filename)
        numeric_movie_name = numeric_movie_match.group(1) if numeric_movie_match else None
        
        # Clean movie name
        clean_title = self.get_clean_title(filename)
        
        if numeric_movie_name and (not clean_title.strip() or clean_title.strip() == "A Space Odyssey"):
            clean_title = f"{numeric_movie_name} {clean_title}"
        
        OutputFormatter.print_file_processing_info("Title", clean_title)
        
        # Transliterate before getting metadata
        original_title = clean_title
        clean_title = Transliterator.transliterate_text(clean_title)
        if original_title != clean_title:
            OutputFormatter.print_file_processing_info("Transliteration", f"{original_title} → {clean_title}")
        
        # Get year and quality
        year, quality = self.get_year_and_quality(filename)
        
        if year:
            OutputFormatter.print_file_processing_info("Year", year)
        if quality:
            OutputFormatter.print_file_processing_info("Quality", quality)
        
        # Get TMDB ID
        tmdb_id_info = (None, year)
        if Config.TMDB_ENABLED:
            OutputFormatter.print_file_processing_info("TMDB Search", clean_title)
            tmdb_id_info = self.get_tmdb_id(clean_title, year, filename)
        
        # Check if user skipped in interactive mode
        if tmdb_id_info is None and Config.INTERACTIVE_MODE:
            OutputFormatter.print_file_processing_result(
                success=False,
                message="Skipped by user. File will not be processed."
            )
            return False
        
        tmdb_id, year = tmdb_id_info if tmdb_id_info else (None, year)
        
        # Format filename using shared formatter
        new_filename = FilenameFormatter.format_movie_filename(
            title=clean_title,
            year=year,
            tmdb_id=tmdb_id,
            quality=quality,
            extension=extension
        )
        
        # Move file
        from ..utils import FileOps
        FileOps.ensure_dir(Config.FILMS)
        destination = os.path.join(Config.FILMS, new_filename)
        
        OutputFormatter.print_file_processing_info("New Filename", new_filename)
        OutputFormatter.print_file_processing_info("Destination", destination)
        
        result = FileOps.move_file(file_path, destination)
        
        OutputFormatter.print_file_processing_result(
            success=result,
            message="Movie processed successfully" if result else "Failed to process movie",
            details={
                "From": file_path,
                "To": destination
            }
        )
        
        return result