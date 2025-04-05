#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quality detector for JFMO
"""

import re


class QualityDetector:
    """Detects video quality from filenames"""
    
    @staticmethod
    def get_quality(filename):
        """
        Extract video quality from filename
        
        Args:
            filename (str): Filename to check
            
        Returns:
            str: Quality string in format [XXXp] or empty string if not found
        """
        # Standard HD/UHD resolutions (480p, 720p, 1080p, 2160p, 4320p)
        match = re.search(r'(480|720|1080|2160|4320)p', filename)
        if match:
            return f"[{match.group(0)}]"
        
        # Cyrillic 'p' character (like 352р)
        match = re.search(r'(240|352|480|576|720|1080|2160|4320)р', filename)
        if match:
            # Convert to standard format with Latin 'p'
            return f"[{match.group(1)}p]"
            
        # Resolution patterns (e.g., 1920x1080)
        res_patterns = [
            (r'1920\s*[xX]\s*1080', "1080p"),
            (r'1280\s*[xX]\s*720', "720p"),
            (r'3840\s*[xX]\s*2160', "2160p"),
            (r'7680\s*[xX]\s*4320', "4320p"),
            (r'720\s*[xX]\s*480', "480p"),
            (r'720\s*[xX]\s*576', "576p")
        ]
        
        for pattern, quality in res_patterns:
            if re.search(pattern, filename):
                return f"[{quality}]"
        
        # Handle SD quality notations
        if re.search(r'\bSD\b', filename, re.IGNORECASE):
            return "[480p]"
        
        # Handle HD/FHD/UHD/QHD quality notations
        hd_patterns = [
            (r'\bHD\b|\b720p\b', "720p"),
            (r'\bFHD\b|\b1080p\b', "1080p"),
            (r'\bQHD\b|\b1440p\b', "1440p"),
            (r'\bUHD\b|\b4K\b|\b2160p\b', "2160p"),
            (r'\b8K\b|\b4320p\b', "4320p")
        ]
        
        for pattern, quality in hd_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return f"[{quality}]"
        
        # If no standard resolution found, check for other resolution indicators
        if re.search(r'[0-9]{3,4}x[0-9]{3,4}', filename, re.IGNORECASE):
            return "[custom]"
            
        return ""