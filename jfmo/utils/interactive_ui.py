#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interactive UI module for JFMO
"""

import sys
import os
from typing import List, Dict, Any, Optional

from .colors import Colors
from .output_formatter import OutputFormatter
from ..config import Config


class InteractiveUI:
    """Interactive UI for user selections"""
    
    @staticmethod
    def clear_screen():
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def _get_input(prompt: str) -> str:
        """Get user input with proper handling"""
        try:
            return input(prompt).strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled by user")
            sys.exit(1)
    
    @classmethod
    def select_media_option(cls, 
                          title: str, 
                          options: List[Dict[str, Any]], 
                          media_type: str = "movie",
                          filename: str = None) -> Optional[Dict[str, Any]]:
        """
        Present media options to the user and get their selection
        
        Args:
            title (str): Original title/query
            options (List[Dict]): List of media options from TMDB
            media_type (str): Type of media ('movie' or 'tv')
            filename (str, optional): Original filename
            
        Returns:
            Dict or None: Selected option or None if skipped
        """
        if not options:
            return None
            
        # If only one option, return it without prompting
        if len(options) == 1:
            return options[0]
            
        # Print header
        print("\n" + OutputFormatter.HORIZONTAL_DIVIDER)
        media_str = "Movie" if media_type == "movie" else "TV Show"
        print(f"{Colors.GREEN}MULTIPLE {media_str.upper()} MATCHES FOUND{Colors.NC}")
        
        if filename:
            OutputFormatter.print_file_processing_info("Original File", filename, indentation=0)
        OutputFormatter.print_file_processing_info("Search Query", title, indentation=0)
        print(OutputFormatter.HORIZONTAL_DIVIDER)
        
        # Print available options with more details
        for i, option in enumerate(options, 1):
            if media_type == "movie":
                title_field = "title"
                date_field = "release_date"
            else:
                title_field = "name"
                date_field = "first_air_date"
                
            title_text = option.get(title_field, "Unknown Title")
            year_text = option.get(date_field, "")[:4] if option.get(date_field) else "????"
            id_text = option.get("id", "")
            popularity = option.get("popularity", 0)
            
            # Highlight the recommended option (first one)
            prefix = f"{Colors.GREEN}[{i}]{Colors.NC}"
            if i == 1:
                prefix = f"{Colors.GREEN}[{i}] (Recomendado){Colors.NC}"
                
            print(f"{prefix} {title_text} ({year_text}) [tmdbid-{id_text}]")
            
            # Print overview if available
            overview = option.get("overview", "")
            if overview:
                # Truncate overview if it's too long
                if len(overview) > 100:
                    overview = overview[:97] + "..."
                print(f"    {Colors.BLUE}Overview:{Colors.NC} {overview}")
                
            # Print popularity score for additional context
            print(f"    {Colors.BLUE}Popularidad:{Colors.NC} {popularity:.1f}")
                
        # Print navigation options
        print(OutputFormatter.SECTION_DIVIDER)
        print(f"{Colors.YELLOW}[s]{Colors.NC} Skip (leave file untouched)")
        print(f"{Colors.YELLOW}[q]{Colors.NC} Quit")
        print(OutputFormatter.SECTION_DIVIDER)
        
        # Get user selection
        while True:
            choice = cls._get_input(f"Please select an option [1-{len(options)}, s, q]: ")
            
            if choice == 'q':
                print(f"{Colors.RED}Operation cancelled by user{Colors.NC}")
                sys.exit(0)
            elif choice == 's':
                return None
            elif choice == '':  # Empty input (just pressed Enter)
                return options[0]  # Select the first (recommended) option
            elif choice.isdigit() and 1 <= int(choice) <= len(options):
                return options[int(choice) - 1]
            else:
                print(f"{Colors.RED}Invalid choice. Please try again.{Colors.NC}")

    @classmethod
    def confirm_action(cls, message: str, default: bool = True) -> bool:
        """
        Ask user to confirm an action
        
        Args:
            message (str): Message to display
            default (bool): Default value if user just presses Enter
            
        Returns:
            bool: True if confirmed, False otherwise
        """
        default_str = "Y/n" if default else "y/N"
        choice = cls._get_input(f"{message} [{default_str}]: ")
        
        if not choice:
            return default
            
        return choice.lower() in ('y', 'yes')