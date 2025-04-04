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
        """Extract video quality from filename"""
        # Look for quality patterns like 1080p, 2160p, etc.
        match = re.search(r'(480|720|1080|2160|4320)p', filename)
        if match:
            return f"[{match.group(0)}]"
        return ""
