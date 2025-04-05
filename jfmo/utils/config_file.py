#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration file handling for JFMO
"""

import os
import json
from ..config import Config
from .colors import Colors
from .logger import Logger


class ConfigFileHandler:
    """Handler for reading and writing configuration files"""
    
    CONFIG_TEMPLATE = {
        "directories": {
            "media_dir": "/data/media",
            "downloads": "/data/media/downloads",
            "films": "/data/media/films",
            "series": "/data/media/series"
        },
        "permissions": {
            "user": "jellyfin",
            "group": "media"
        },
        "tmdb": {
            "api_key": "",
            "enabled": True
        },
        "logging": {
            "log_file": "/tmp/jfmo.log",
            "verbose": True
        },
        "options": {
            "interactive": True
        }
    }
    
    @classmethod
    def create_template(cls, output_path):
        """
        Create a template configuration file
        
        Args:
            output_path (str): Path where to save the template
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Write the template
            with open(output_path, 'w') as f:
                json.dump(cls.CONFIG_TEMPLATE, f, indent=4)
                
            print(f"{Colors.GREEN}✓ Configuration template created at:{Colors.NC} {output_path}")
            return True
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to create configuration template: {str(e)}{Colors.NC}")
            return False
    
    @classmethod
    def read_config(cls, config_path):
        """
        Read configuration from a file
        
        Args:
            config_path (str): Path to the configuration file
        
        Returns:
            dict: Configuration values
        """
        if not os.path.exists(config_path):
            print(f"{Colors.RED}✗ Configuration file not found: {config_path}{Colors.NC}")
            return None
            
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                
            print(f"{Colors.GREEN}✓ Configuration loaded from:{Colors.NC} {config_path}")
            return config_data
        except json.JSONDecodeError:
            print(f"{Colors.RED}✗ Invalid JSON in configuration file{Colors.NC}")
            return None
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to read configuration: {str(e)}{Colors.NC}")
            return None
    
    @classmethod
    def update_config_from_file(cls, config_path):
        """
        Update global config from file
        
        Args:
            config_path (str): Path to the configuration file
            
        Returns:
            bool: True if successful, False otherwise
        """
        config_data = cls.read_config(config_path)
        if not config_data:
            return False
        
        try:
            # Update directory settings
            if 'directories' in config_data:
                dirs = config_data['directories']
                if 'media_dir' in dirs:
                    Config.MEDIA_DIR = dirs['media_dir']
                if 'downloads' in dirs:
                    Config.DOWNLOADS = dirs['downloads']
                if 'films' in dirs:
                    Config.FILMS = dirs['films']
                if 'series' in dirs:
                    Config.SERIES = dirs['series']
            
            # Update permission settings
            if 'permissions' in config_data:
                perms = config_data['permissions']
                if 'user' in perms:
                    Config.MEDIA_USER = perms['user']
                if 'group' in perms:
                    Config.MEDIA_GROUP = perms['group']
            
            # Update TMDB settings
            if 'tmdb' in config_data:
                tmdb = config_data['tmdb']
                if 'api_key' in tmdb and tmdb['api_key']:
                    Config.TMDB_API_KEY = tmdb['api_key']
                if 'enabled' in tmdb:
                    Config.TMDB_ENABLED = tmdb['enabled']
            
            # Update logging settings
            if 'logging' in config_data:
                logging = config_data['logging']
                if 'log_file' in logging:
                    Config.LOG_FILE = logging['log_file']
                if 'verbose' in logging:
                    Config.VERBOSE = logging['verbose']
                    
            # Update options
            if 'options' in config_data:
                options = config_data['options']
                if 'interactive' in options:
                    Config.INTERACTIVE_MODE = options['interactive']
            
            return True
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to apply configuration: {str(e)}{Colors.NC}")
            Logger.error(f"Failed to apply configuration: {str(e)}")
            return False
    
    @classmethod
    def get_default_config_path(cls):
        """Get the default configuration file path"""
        # Try in this order:
        # 1. ~/.config/jfmo/config.json
        # 2. /etc/jfmo/config.json
        # 3. ./config.json
        
        home_config = os.path.expanduser("~/.config/jfmo/config.json")
        system_config = "/etc/jfmo/config.json"
        local_config = "./config.json"
        
        if os.path.exists(home_config):
            return home_config
        elif os.path.exists(system_config):
            return system_config
        elif os.path.exists(local_config):
            return local_config
            
        return None