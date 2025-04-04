#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File operations module for JFMO
"""

import os
import shutil
import subprocess
from ..config import Config
from .colors import Colors
from .logger import Logger


class FileOps:
    """File operations class for JFMO"""
    
    @staticmethod
    def clean_name(name):
        """Clean name by removing special characters and prefixes"""
        import re
        
        # Remove extension if present
        name = os.path.splitext(name)[0]
        
        # Remove prefixes in brackets like [NOOBDL]
        name = re.sub(r'\[[^\]]*\]', '', name)
        
        # Remove suffixes like "- LostFilm.TV" or similar
        name = re.sub(r' ?- ?LostFilm\.TV.*', '', name)

        # Remove alternative titles in parentheses
        name = re.sub(r' ?\([^)]+\)', '', name)
        
        # Convert dots, hyphens and underscores to spaces
        name = name.replace('.', ' ').replace('_', ' ').replace('-', ' ').replace('*', '')
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove quality tags like "2160p", "WEB-DL", "SDR", etc.
        name = re.sub(r' (480|720|1080|2160|4320)p', '', name)
        name = re.sub(r' (WEB|WEB-DL|WEBDL|HDR|SDR|BDRip).*', '', name)
        
        return name
    
    @staticmethod
    def set_permissions(path, is_dir=False):
        """Set correct permissions and ownership"""
        if Config.TEST_MODE:
            return
        
        try:
            # Set ownership
            if os.path.exists(path):
                subprocess.run(['chown', f"{Config.MEDIA_USER}:{Config.MEDIA_GROUP}", path], check=True)
                
                # Set permissions
                if is_dir:
                    subprocess.run(['chmod', '775', path], check=True)  # rwxrwxr-x
                else:
                    subprocess.run(['chmod', '664', path], check=True)  # rw-rw-r--
        except subprocess.SubprocessError as e:
            print(Colors.red(f"Error setting permissions: {str(e)}"))
            Logger.error(f"Error setting permissions for {path}: {str(e)}")
    
    @staticmethod
    def ensure_dir(directory):
        """Create directory if it doesn't exist and set permissions"""
        if not os.path.exists(directory) and not Config.TEST_MODE:
            try:
                os.makedirs(directory, exist_ok=True)
                FileOps.set_permissions(directory, is_dir=True)
                return True
            except Exception as e:
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
        
        print(f"{Colors.BLUE}{'Would move' if Config.TEST_MODE else 'Moving'}:{Colors.NC} {source_file} -> {dest_file}")
        
        # Move the file
        if not Config.TEST_MODE:
            try:
                shutil.move(source_file, dest_file)
                FileOps.set_permissions(dest_file)
                print(f"{Colors.GREEN}✓ Success{Colors.NC}")
                Logger.info(f"MOVING: {source_file} -> {dest_file} (success)")
                return True
            except Exception as e:
                print(f"{Colors.RED}✗ Error: {str(e)}{Colors.NC}")
                Logger.error(f"ERROR MOVING: {source_file} -> {dest_file} ({str(e)})")
                return False
        else:
            print(f"{Colors.YELLOW}(Test mode - no changes made){Colors.NC}")
            Logger.info(f"TEST - Would move: {source_file} -> {dest_file}")
            return True
    
    @staticmethod
    def remove_empty_dir(directory):
        """Remove an empty directory"""
        if not Config.TEST_MODE and os.path.exists(directory) and not os.listdir(directory):
            try:
                os.rmdir(directory)
                print(f"{Colors.YELLOW}Removed empty directory:{Colors.NC} {directory}")
                Logger.info(f"REMOVED EMPTY DIRECTORY: {directory}")
                return True
            except Exception as e:
                Logger.error(f"Failed to remove directory {directory}: {str(e)}")
                return False
        return False
    
    @staticmethod
    def is_video_file(filename):
        """Check if file is a video file based on extension"""
        return filename.lower().endswith(Config.VIDEO_EXTENSIONS)
