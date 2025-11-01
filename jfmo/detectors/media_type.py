"""
Media type detection utilities
Centralizes all logic for determining if a file is a movie or series
"""
import re
from typing import Optional, Tuple


class MediaTypeDetector:
    """Detects whether a file is a movie or TV series"""
    
    # Definitive series patterns - these ALWAYS indicate a TV series
    DEFINITIVE_SERIES_PATTERNS = [
        r'S[0-9]{1,2}E[0-9]{1,2}',           # S01E01
        r'S[0-9]{1,2}\.E[0-9]{1,2}',         # S01.E01
        r'\bs[0-9]{1,2}e[0-9]{1,2}\b',       # s01e01
        r'S[0-9]{1,2}E[0-9]{1,2}-E?[0-9]{1,2}',  # S01E01-E02
        r'[0-9]{1,2}[xX][0-9]{1,2}'          # 3x07
    ]
    
    # Ambiguous patterns that need additional context
    AMBIGUOUS_PATTERNS = [
        (r'[Ee]pisode[. ]([0-9]{1,2})', "Episode X format"),
        (r'(?<![0-9])([0-9]{1})([0-9]{2})(?![0-9])', "Combined season/episode (NNN)"),
        (r'(19|20)[0-9]{2}[.-][0-9]{2}[.-][0-9]{2}', "Date-based format"),
    ]
    
    # Movie indicators
    MOVIE_PATTERNS = [
        r'(19|20)[0-9]{2}.*\b(720p|1080p|2160p|HDR|BluRay)\b'
    ]
    
    @classmethod
    def is_series(cls, filename: str) -> bool:
        """
        Check if filename represents a TV series
        
        Args:
            filename: The filename to check
            
        Returns:
            bool: True if it's a series
        """
        # Check definitive patterns first
        for pattern in cls.DEFINITIVE_SERIES_PATTERNS:
            if re.search(pattern, filename, re.IGNORECASE):
                return True
        
        # Check if it looks like a movie (year + quality)
        for pattern in cls.MOVIE_PATTERNS:
            if re.search(pattern, filename, re.IGNORECASE):
                return False
        
        # If starts with year and has season pattern, it's a series (like 1923.S01E01)
        if re.match(r'^[12][0-9]{3}\.S[0-9]{1,2}', filename):
            return True
        
        return False
    
    @classmethod
    def is_ambiguous(cls, filename: str) -> Tuple[bool, str]:
        """
        Check if filename has ambiguous patterns that should be skipped
        
        Args:
            filename: The filename to check
            
        Returns:
            Tuple[bool, str]: (is_ambiguous, reason)
        """
        # Don't skip if it has definitive series patterns
        for pattern in cls.DEFINITIVE_SERIES_PATTERNS:
            if re.search(pattern, filename, re.IGNORECASE):
                return False, ""
        
        # Check ambiguous patterns
        for pattern, reason in cls.AMBIGUOUS_PATTERNS:
            if re.search(pattern, filename, re.IGNORECASE):
                # Exception: NNN pattern with year+quality is likely a movie
                if pattern == cls.AMBIGUOUS_PATTERNS[1][0]:
                    if re.search(r'(19|20)[0-9]{2}.*\b(720|1080|2160)p\b', filename, re.IGNORECASE):
                        continue
                
                return True, reason
        
        return False, ""