#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Movie processor for JFMO
"""

import os
from ..config import Config
from ..utils import FileOps, Colors, Logger
from .media_processor import MediaProcessor


class MovieProcessor(MediaProcessor):
    """Class for processing movie files"""
    
    def process(self, file_path):
        """Process a movie file"""
        filename = os.path.basename(file_path)
        Logger.info(f"Processing movie: {filename}")
        
        # Clean movie name and get metadata
        base_title = self.get_clean_title(filename)
        year, quality = self.get_year_and_quality(filename)
        
        # Remove year from title if it exists
        if year:
            base_title = base_title.replace(f" {year}", "")
        
        # Format movie name with appropriate format
        extension = os.path.splitext(filename)[1]
        if year:
            if quality:
                new_filename = f"{base_title} ({year}) - {quality}{extension}"
            else:
                new_filename = f"{base_title} ({year}){extension}"
        else:
            if quality:
                new_filename = f"{base_title} - {quality}{extension}"
            else:
                new_filename = f"{base_title}{extension}"
        
        # Ensure films directory exists
        FileOps.ensure_dir(Config.FILMS)
        
        # Move file
        return FileOps.move_file(file_path, os.path.join(Config.FILMS, new_filename))
