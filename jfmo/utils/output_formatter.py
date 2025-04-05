#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Output formatting utilities for JFMO
"""

import os
import shutil
from typing import Dict, List, Optional, Tuple, Any

from .colors import Colors
from ..config import Config


class OutputFormatter:
    """Class for formatting console output"""
    
    # Terminal width detection
    try:
        TERM_WIDTH = shutil.get_terminal_size().columns
    except:
        TERM_WIDTH = 80  # Default width
    
    HORIZONTAL_DIVIDER = "━" * TERM_WIDTH
    SECTION_DIVIDER = "─" * TERM_WIDTH
    
    @classmethod
    def print_header(cls):
        """Print main program header"""
        print("\n" + cls.HORIZONTAL_DIVIDER)
        print(f"{Colors.GREEN}JELLYFIN FORMAT MEDIA ORGANIZER (JFMO){Colors.NC}")
        print(f"{Colors.GREEN}Version: {Config.VERSION}{Colors.NC}")
        print(cls.HORIZONTAL_DIVIDER + "\n")
        
        if Config.TEST_MODE:
            print(f"{Colors.YELLOW}MODE: TEST{Colors.NC} - No actual file operations will be performed")
        else:
            print(f"{Colors.YELLOW}MODE: LIVE{Colors.NC} - Files will be moved to their destinations")
        
        print("")
        print(f"{Colors.BLUE}📂 Downloads directory:{Colors.NC} {Config.DOWNLOADS}")
        print(f"{Colors.BLUE}🎥 Movies directory:{Colors.NC} {Config.FILMS}")
        print(f"{Colors.BLUE}📺 TV Shows directory:{Colors.NC} {Config.SERIES}")
        print(f"{Colors.BLUE}👤 Media ownership:{Colors.NC} {Config.MEDIA_USER}:{Config.MEDIA_GROUP}")
        print(f"{Colors.BLUE}🔤 Transliteration:{Colors.NC} Enabled")
        
        if Config.INTERACTIVE_MODE:
            interactive_status = f"{Colors.GREEN}Enabled{Colors.NC}"
        else:
            interactive_status = f"{Colors.YELLOW}Disabled{Colors.NC} (automatic mode)"
        print(f"{Colors.BLUE}🔄 Interactive Mode:{Colors.NC} {interactive_status}")
        
        if Config.TMDB_ENABLED:
            api_status = f"{Colors.GREEN}Configured ✓{Colors.NC}" if Config.TMDB_API_KEY else f"{Colors.RED}Not configured ✗{Colors.NC}"
            print(f"{Colors.BLUE}🎬 TMDB Integration:{Colors.NC} Enabled ({api_status})")
        else:
            print(f"{Colors.BLUE}🎬 TMDB Integration:{Colors.NC} {Colors.YELLOW}Disabled{Colors.NC}")
            
        print(f"{Colors.BLUE}📄 Log file:{Colors.NC} {Config.LOG_FILE}")
        print("")
    
    @classmethod
    def print_directory_header(cls, dir_name: str, dir_type: str, action: str):
        """
        Print a header for directory processing
        
        Args:
            dir_name (str): Name of the directory
            dir_type (str): Type of directory (e.g., "TV show directory")
            action (str): Action being performed
        """
        print("\n" + cls.HORIZONTAL_DIVIDER)
        print(f"{Colors.BLUE}📁 PROCESSING {dir_type.upper()}: {dir_name}{Colors.NC}")
        print(cls.HORIZONTAL_DIVIDER)
        print(f"{Colors.YELLOW}Action:{Colors.NC} {action}")
        print("")
    
    @classmethod
    def print_section_header(cls, title: str):
        """Print a section header"""
        print("\n" + cls.SECTION_DIVIDER)
        print(f"{Colors.GREEN}=== {title} ==={Colors.NC}")
        print("")
    
    @classmethod
    def print_file_processing_header(cls, filename: str):
        """Print header for file processing"""
        print(f"{Colors.BLUE}▶ {filename}{Colors.NC}")
    
    @classmethod
    def print_file_processing_result(cls, 
                                   success: Optional[bool], 
                                   message: str, 
                                   details: Optional[Dict[str, str]] = None, 
                                   indentation: int = 2):
        """
        Print file processing result
        
        Args:
            success (bool or None): Whether the operation was successful, None for skipped
            message (str): Message to display
            details (dict, optional): Additional details to display
            indentation (int): Number of spaces to indent
        """
        indent = " " * indentation
        if success is True:
            status = f"{Colors.GREEN}✅ SUCCESS:{Colors.NC}"
        elif success is False:
            status = f"{Colors.RED}❌ ERROR:{Colors.NC}"
        else:  # success is None, indicates a skip
            status = f"{Colors.YELLOW}⏩ SKIPPED:{Colors.NC}"
            
        print(f"{indent}{status} {message}")
        
        if details:
            for key, value in details.items():
                print(f"{indent}{Colors.YELLOW}{key}:{Colors.NC} {value}")
                
        print("")
    
    @classmethod
    def print_file_processing_info(cls, label: str, value: str, indentation: int = 2):
        """Print file processing info line"""
        indent = " " * indentation
        print(f"{indent}{Colors.BLUE}🔍 {label}:{Colors.NC} {value}")
    
    @classmethod
    def print_summary(cls, stats: Dict[str, int]):
        """Print summary statistics"""
        print("\n" + cls.HORIZONTAL_DIVIDER)
        print(f"{Colors.GREEN}✅ PROCESSING SUMMARY{Colors.NC}")
        print(cls.HORIZONTAL_DIVIDER)
        
        print(f"{Colors.BLUE}Files processed:{Colors.NC} {stats.get('total', 0)}")
        print(f"{Colors.GREEN}Successful:{Colors.NC} {stats.get('success', 0)}")
        print(f"{Colors.RED}Errors:{Colors.NC} {stats.get('error', 0)}")
        print(f"{Colors.YELLOW}Skipped:{Colors.NC} {stats.get('skipped', 0)}")
        
        if Config.TEST_MODE:
            print(f"\n{Colors.YELLOW}Note: This was a test run. No files were actually modified.{Colors.NC}")
            print(f"{Colors.YELLOW}To perform actual changes, run without the --test flag.{Colors.NC}")
            
        print(f"\n{Colors.BLUE}A detailed log has been saved at: {Config.LOG_FILE}{Colors.NC}")
        print("")