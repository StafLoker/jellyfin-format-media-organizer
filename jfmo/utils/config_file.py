import os
import yaml
from pathlib import Path


class ConfigFileHandler:
    """Handler for reading and writing configuration files"""
    
    CONFIG_TEMPLATE = """# JFMO Configuration File
# Jellyfin Format Media Organizer

# Directory Configuration
directories:
  media_dir: /data/media
  downloads: /data/media/downloads
  films: /data/media/films
  series: /data/media/series
  incomplete: /data/media/incomplete  # Optional: directory with incomplete downloads

# File Permissions
permissions:
  user: jellyfin
  group: media

# TMDB Integration
tmdb:
  api_key: ""  # Get your API key from https://www.themoviedb.org/settings/api
  enabled: false

# Logging Configuration
logging:
  log_file: /tmp/jfmo.log
  verbose: false

# Processing Options
options:
  interactive: true  # Show interactive prompts for ambiguous matches (auto-disabled in daemon mode)

# Daemon Mode Options
daemon:
  enabled: false  # Run as daemon (watch directory for new files)
  check_interval: 10  # Seconds between directory checks
"""
    
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
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the template
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cls.CONFIG_TEMPLATE)
                
            print(f"\033[0;32mâœ“ Configuration template created at:\033[0m {output_path}")
            return True
        except Exception as e:
            print(f"\033[0;31mâœ— Failed to create configuration template: {str(e)}\033[0m")
            return False
    
    @classmethod
    def read_config(cls, config_path):
        """
        Read configuration from a YAML file
        
        Args:
            config_path (str): Path to the configuration file
        
        Returns:
            dict: Configuration values
        """
        if not os.path.exists(config_path):
            print(f"\033[0;31mâœ— Configuration file not found: {config_path}\033[0m")
            return None
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                
            print(f"\033[0;32mâœ“ Configuration loaded from:\033[0m {config_path}")
            return config_data
        except yaml.YAMLError as e:
            print(f"\033[0;31mâœ— Invalid YAML in configuration file: {str(e)}\033[0m")
            return None
        except Exception as e:
            print(f"\033[0;31mâœ— Failed to read configuration: {str(e)}\033[0m")
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
        # Import here to avoid circular imports
        from ..config import Config
        from .logger import Logger
        
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
                if 'incomplete' in dirs:
                    Config.INCOMPLETE_DIR = dirs['incomplete']
            
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
            
            # Update daemon settings
            if 'daemon' in config_data:
                daemon = config_data['daemon']
                if 'enabled' in daemon:
                    Config.DAEMON_MODE = daemon['enabled']
                if 'check_interval' in daemon:
                    Config.DAEMON_INTERVAL = daemon['check_interval']
            
            return True
        except Exception as e:
            print(f"\033[0;31mâœ— Failed to apply configuration: {str(e)}\033[0m")
            Logger.error(f"Failed to apply configuration: {str(e)}")
            return False
            
    @classmethod
    def get_default_config_path(cls):
        """Get the default configuration file path"""
        # Try in this order:
        # 1. ~/.config/jfmo/config.yaml
        # 2. ~/.config/jfmo/config.yml
        # 3. /etc/jfmo/config.yaml
        # 4. /etc/jfmo/config.yml
        # 5. ./config.yaml
        # 6. ./config.yml
        
        config_paths = [
            os.path.expanduser("~/.config/jfmo/config.yaml"),
            os.path.expanduser("~/.config/jfmo/config.yml"),
            "/etc/jfmo/config.yaml",
            "/etc/jfmo/config.yml",
            "./config.yaml",
            "./config.yml"
        ]
        
        for config_path in config_paths:
            if os.path.exists(config_path):
                return config_path
            
        return None