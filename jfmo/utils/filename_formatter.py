"""
Utilities for formatting media filenames consistently
"""
from typing import Optional


class FilenameFormatter:
    """Formats media filenames according to Jellyfin standards"""
    
    @staticmethod
    def format_movie_filename(title: str, 
                            year: Optional[str] = None, 
                            tmdb_id: Optional[int] = None, 
                            quality: Optional[str] = None,
                            extension: str = ".mkv") -> str:
        """
        Format movie filename
        
        Args:
            title: Movie title
            year: Release year
            tmdb_id: TMDB ID
            quality: Quality tag (e.g., "[1080p]")
            extension: File extension
            
        Returns:
            str: Formatted filename
        """
        parts = [title]
        
        if year:
            parts.append(f"({year})")
        
        if tmdb_id:
            parts.append(f"[tmdbid-{tmdb_id}]")
        
        if quality:
            parts.append(f"- {quality}")
        
        return " ".join(parts) + extension
    
    @staticmethod
    def format_series_filename(series_name: str,
                              season: str,
                              episode: str,
                              quality: Optional[str] = None,
                              extension: str = ".mkv") -> str:
        """
        Format series episode filename
        
        Args:
            series_name: Series title
            season: Season number (already formatted as "01")
            episode: Episode number
            quality: Quality tag (e.g., "[1080p]")
            extension: File extension
            
        Returns:
            str: Formatted filename
        """
        filename = f"{series_name} S{season}E{episode}"
        
        if quality:
            filename += f" - {quality}"
        
        return filename + extension
    
    @staticmethod
    def format_series_directory(series_name: str,
                               year: Optional[str] = None,
                               tmdb_id: Optional[int] = None) -> str:
        """
        Format series directory name
        
        Args:
            series_name: Series title
            year: First air year
            tmdb_id: TMDB ID
            
        Returns:
            str: Formatted directory name
        """
        parts = [series_name]
        
        if year:
            parts.append(f"({year})")
        
        if tmdb_id:
            parts.append(f"[tmdbid-{tmdb_id}]")
        
        return " ".join(parts)