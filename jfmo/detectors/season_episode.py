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
        """Detect season and episode numbers from filename"""
        # Pattern 1: S01E01
        match = re.search(r'[Ss]([0-9]{1,2})[Ee]([0-9]{1,2})', filename)
        if match:
            return (match.group(1), match.group(2))
        
        # Pattern 2: S01.E01
        match = re.search(r'[Ss]([0-9]{1,2})\.?[Ee]([0-9]{1,2})', filename)
        if match:
            return (match.group(1), match.group(2))
        
        # Pattern 3: Detect "La Casa de Papel 3" where 3 is the season
        match = re.search(r'Casa de Papel ([0-9]{1})', filename)
        if match:
            return (match.group(1), "00")  # No specific episode, use 00 as default
        
        return None
