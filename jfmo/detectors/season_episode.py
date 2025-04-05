#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Season/Episode detector for JFMO
"""

import re
from typing import Optional, Tuple


class SeasonEpisodeDetector:
    """Detects season and episode numbers from filenames"""
    
    @staticmethod
    def detect(filename) -> Optional[Tuple[str, str]]:
        """
        Detect season and episode numbers from filename
        
        Args:
            filename (str): Filename to check
            
        Returns:
            Tuple[str, str] or None: (season, episode) if found, None otherwise
        """
        # Pattern 1: Standard SxxExx (case-insensitive)
        match = re.search(r'[Ss]([0-9]{1,2})[Ee]([0-9]{1,2})', filename)
        if match:
            return (match.group(1), match.group(2))
        
        # Pattern 2: Standard S01.E01 (with dot, case-insensitive)
        match = re.search(r'[Ss]([0-9]{1,2})\.?[Ee]([0-9]{1,2})', filename)
        if match:
            return (match.group(1), match.group(2))
            
        # Pattern 3: Lowercase sXXeXX (e.g., s01e07)
        match = re.search(r'\bs([0-9]{1,2})e([0-9]{1,2})\b', filename.lower())
        if match:
            return (match.group(1), match.group(2))
            
        # Pattern 4: 3x07 or 3X07 format (season x episode)
        match = re.search(r'(?<![0-9])([0-9]{1,2})[xX]([0-9]{1,2})(?![0-9])', filename)
        if match:
            return (match.group(1), match.group(2))
            
        # Pattern 5: Multi-episode format (S01E01-E02 or S01E01-02)
        # For these, we just use the first episode
        match = re.search(r'[Ss]([0-9]{1,2})[Ee]([0-9]{1,2})-[Ee]?[0-9]{1,2}', filename)
        if match:
            return (match.group(1), match.group(2))
            
        # Pattern 6: Season number in format "s01" in directory name
        # (Used with season_only=True in detect_season_only method)
        match = re.search(r'\bs([0-9]{1,2})\b', filename.lower())
        if match:
            # Return only when specifically requesting this pattern
            # See detect_season_only method below
            pass
        
        # Pattern 7: Combined season/episode like 308 (s03e08)
        match = re.search(r'(?<![0-9])([0-9]{1})([0-9]{2})(?![0-9])', filename)
        if match and 0 < int(match.group(1)) < 30 and 0 < int(match.group(2)) < 100:
            # Check if this could reasonably be a season/episode (avoid false positives)
            # Most shows don't go beyond season 30, and episodes don't go beyond 99
            return (match.group(1), match.group(2))
        
        # Pattern 8: Detect "La Casa de Papel 3" where 3 is the season
        match = re.search(r'Casa de Papel ([0-9]{1})', filename)
        if match:
            return (match.group(1), "00")  # No specific episode, use 00 as default
        
        # Pattern 9: Episode without season (e.g., "Episode 5")
        # We don't include this by default as it's too ambiguous
        # If needed, implement with specific context checks
        
        return None
    
    @staticmethod
    def detect_season_only(directory_name) -> Optional[str]:
        """
        Detect only season number from directory name
        
        Args:
            directory_name (str): Directory name to check
            
        Returns:
            str or None: Season number if found, None otherwise
        """
        # Look for season in format "s01" in directory name
        match = re.search(r'\bs([0-9]{1,2})\b', directory_name.lower())
        if match:
            return match.group(1)
            
        # Other season-only patterns can be added here
        
        return None
        
    @staticmethod
    def detect_episode_only(filename) -> Optional[str]:
        """
        Detect only episode number from filename when season is known
        
        Args:
            filename (str): Filename to check
            
        Returns:
            str or None: Episode number if found, None otherwise
        """
        # Look for episode in standard format (e01, E01, etc.)
        match = re.search(r'[Ee]([0-9]{1,2})', filename)
        if match:
            return match.group(1)
            
        # Look for episode in format "Episode X" or "Episode.X"
        match = re.search(r'[Ee]pisode[.\s-]*([0-9]{1,2})', filename, re.IGNORECASE)
        if match:
            return match.group(1)
            
        # Look for episode as a number at the end of filename before extension
        match = re.search(r'([0-9]{1,2})\.[^.]+$', filename)
        if match:
            return match.group(1)
            
        return None