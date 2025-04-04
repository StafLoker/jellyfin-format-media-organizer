#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Year detector for JFMO
"""

import re


class YearDetector:
    """Detects year values from filenames"""
    
    @staticmethod
    def get_year(filename):
        """Extract the year from a filename"""
        # Look for year pattern (4 digits between 1900-2030)
        match = re.search(r'(19[0-9]{2}|20[0-3][0-9])', filename)
        if match:
            return match.group(0)
        return ""
