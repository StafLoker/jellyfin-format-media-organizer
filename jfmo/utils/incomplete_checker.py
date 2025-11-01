"""
Utilities for handling incomplete episodes
"""
import os
import re
from typing import Optional
from ..config import Config
from .file_ops import FileOps
from .logger import Logger


class IncompleteChecker:
    """Handles checking for incomplete episodes"""
    
    @staticmethod
    def has_incomplete_episodes(series_name: str, season_num: str, incomplete_dir: Optional[str] = None) -> bool:
        """
        Check if series has incomplete episodes in incomplete directory
        
        Args:
            series_name: Name of the series
            season_num: Season number (e.g., "01")
            incomplete_dir: Directory with incomplete downloads (optional, uses Config if not provided)
            
        Returns:
            bool: True if incomplete episodes exist
        """
        check_dir = incomplete_dir or Config.INCOMPLETE_DIR
        
        if not check_dir or not os.path.exists(check_dir):
            return False
        
        try:
            # Normalize series name for comparison
            series_lower = series_name.lower().replace(' ', '').replace('.', '')
            
            for filename in os.listdir(check_dir):
                if not FileOps.is_video_file(filename):
                    continue
                
                # Check if filename matches series and season
                filename_lower = filename.lower().replace(' ', '').replace('.', '')
                
                # Look for season pattern
                season_pattern = f's{season_num}e[0-9]{{1,2}}'
                
                if (series_lower in filename_lower and 
                    re.search(season_pattern, filename_lower)):
                    Logger.info(f"Found incomplete episode: {filename}")
                    return True
            
            return False
        except Exception as e:
            Logger.error(f"Error checking incomplete episodes: {e}")
            return False