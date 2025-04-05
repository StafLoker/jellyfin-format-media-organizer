#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Base media processor class for JFMO
"""

from ..utils import FileOps, Transliterator
from ..detectors import YearDetector, QualityDetector


class MediaProcessor:
    """Base class for media processing"""
    
    def __init__(self):
        """Initialize the processor"""
        pass
    
    def get_clean_title(self, filename):
        """Get a clean title from filename with possible transliteration"""
        # Clean name
        clean_title = FileOps.clean_name(filename)
        
        # Try to transliterate
        transliterated = Transliterator.transliterate_text(clean_title)
        
        return transliterated
    
    def get_year_and_quality(self, filename):
        """Get year and quality from filename"""
        year = YearDetector.get_year(filename)
        quality = QualityDetector.get_quality(filename)
        
        return year, quality
    
    def process(self, file_path):
        """Process a media file"""
        raise NotImplementedError("Subclasses must implement this method")