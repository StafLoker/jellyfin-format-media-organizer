#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File operations module for JFMO
"""

import os
import shutil
import subprocess
import re
from ..config import Config
from .colors import Colors
from .logger import Logger
from .output_formatter import OutputFormatter


class FileOps:
    """File operations class for JFMO"""
    
    @staticmethod
    def clean_name(name):
        """Clean name by removing special characters and prefixes"""
        # Remove extension if present
        name = os.path.splitext(name)[0]
        
        # Remove prefixes in brackets like [NOOBDL]
        name = re.sub(r'\[[^\]]*\]', '', name)
        
        # Remove suffixes like "- LostFilm.TV" or similar
        name = re.sub(r' ?- ?LostFilm\.TV.*', '', name)
        name = re.sub(r' ?- ?rus\.?.*', '', name, flags=re.IGNORECASE)  # Russian indicator
        
        # Remove alternative titles in parentheses
        name = re.sub(r' ?\([^)]+\)', '', name)
        
        # Remove season and episode patterns
        name = re.sub(r'S[0-9]{1,2}E[0-9]{1,2}.*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'Season\s*[0-9]{1,2}.*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'[0-9]{1,2}x[0-9]{1,2}.*', '', name, flags=re.IGNORECASE)
        
        # Remove date patterns (YYYY.MM.DD or YYYY-MM-DD)
        name = re.sub(r'(19|20)[0-9]{2}[.\-][0-9]{1,2}[.\-][0-9]{1,2}', '', name)
        
        # Convert dots, hyphens and underscores to spaces
        name = name.replace('.', ' ').replace('_', ' ').replace('-', ' ').replace('*', '')
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove quality tags like "2160p", "WEB-DL", "SDR", etc.
        name = re.sub(r'\b(480|720|1080|2160|4320)p\b', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\b(WEB|WEB-DL|WEBDL|HDR|SDR|BDRip|BluRay|x264|x265|HEVC|H264|H265)\b.*', '', name, flags=re.IGNORECASE)
        
        # Remove year at the end
        name = re.sub(r'\b(19|20)[0-9]{2}\b', '', name)
        
        return name.strip()

    @staticmethod
    def set_permissions(path, is_dir=False):
        """Set correct permissions and ownership"""
        if Config.TEST_MODE:
            return True
        
        try:
            # Set ownership
            if os.path.exists(path):
                subprocess.run(['chown', f"{Config.MEDIA_USER}:{Config.MEDIA_GROUP}", path], check=True)
                
                # Set permissions
                if is_dir:
                    subprocess.run(['chmod', '775', path], check=True)  # rwxrwxr-x
                else:
                    subprocess.run(['chmod', '664', path], check=True)  # rw-rw-r--
            return True
        except subprocess.SubprocessError as e:
            OutputFormatter.print_file_processing_info("Error", f"Setting permissions failed: {str(e)}")
            Logger.error(f"Error setting permissions for {path}: {str(e)}")
            return False
    
    @staticmethod
    def ensure_dir(directory):
        """Create directory if it doesn't exist and set permissions"""
        if not os.path.exists(directory) and not Config.TEST_MODE:
            try:
                os.makedirs(directory, exist_ok=True)
                FileOps.set_permissions(directory, is_dir=True)
                return True
            except Exception as e:
                OutputFormatter.print_file_processing_info("Error", f"Creating directory failed: {str(e)}")
                Logger.error(f"Failed to create directory {directory}: {str(e)}")
                return False
        return True
    
    @staticmethod
    def move_file(source_file, dest_file):
        """Move a file and set the correct permissions"""
        # Create destination directory if it doesn't exist
        dest_dir = os.path.dirname(dest_file)
        if not FileOps.ensure_dir(dest_dir):
            return False
        
        # Handle test mode
        if Config.TEST_MODE:
            action_msg = f"Would move: {source_file} -> {dest_file}"
            OutputFormatter.print_file_processing_info("Test Mode", "No changes made")
            Logger.info(f"TEST - {action_msg}")
            return True
        
        # Actual file move in live mode
        try:
            shutil.move(source_file, dest_file)
            FileOps.set_permissions(dest_file)
            action_msg = f"Moved: {source_file} -> {dest_file}"
            Logger.info(f"MOVING: {source_file} -> {dest_file} (success)")
            return True
        except Exception as e:
            error_msg = f"Error moving file: {str(e)}"
            OutputFormatter.print_file_processing_info("Error", error_msg)
            Logger.error(f"ERROR MOVING: {source_file} -> {dest_file} ({str(e)})")
            return False
    
    @staticmethod
    def remove_empty_dir(directory):
        """Remove an empty directory"""
        if not Config.TEST_MODE and os.path.exists(directory) and not os.listdir(directory):
            try:
                os.rmdir(directory)
                Logger.info(f"REMOVED EMPTY DIRECTORY: {directory}")
                return True
            except Exception as e:
                OutputFormatter.print_file_processing_info("Error", f"Failed to remove directory: {str(e)}")
                Logger.error(f"Failed to remove directory {directory}: {str(e)}")
                return False
        elif Config.TEST_MODE and os.path.exists(directory) and not os.listdir(directory):
            Logger.info(f"TEST - Would remove empty directory: {directory}")
            return True
        return False
    
    @staticmethod
    def is_video_file(filename):
        """Check if file is a video file based on extension"""
        return filename.lower().endswith(Config.VIDEO_EXTENSIONS)