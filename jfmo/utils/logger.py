#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Logging module for JFMO
"""

import logging
from ..config import Config


class Logger:
    """Logger class for JFMO"""
    _logger = None
    
    @classmethod
    def setup(cls):
        """Setup the logger"""
        # Configure logging
        logging.basicConfig(
            filename=Config.LOG_FILE,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        cls._logger = logging.getLogger('jfmo')
        
        # Add console handler if verbose
        if Config.VERBOSE:
            console = logging.StreamHandler()
            console.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(levelname)s - %(message)s')
            console.setFormatter(formatter)
            cls._logger.addHandler(console)
    
    @classmethod
    def log(cls, message, level='info'):
        """Log a message if verbose mode is enabled"""
        if cls._logger is None:
            cls.setup()
            
        if Config.VERBOSE:
            if level.lower() == 'info':
                cls._logger.info(message)
            elif level.lower() == 'warning':
                cls._logger.warning(message)
            elif level.lower() == 'error':
                cls._logger.error(message)
            elif level.lower() == 'debug':
                cls._logger.debug(message)
    
    @classmethod
    def info(cls, message):
        """Log an info message"""
        cls.log(message, 'info')
    
    @classmethod
    def warning(cls, message):
        """Log a warning message"""
        cls.log(message, 'warning')
    
    @classmethod
    def error(cls, message):
        """Log an error message"""
        cls.log(message, 'error')
    
    @classmethod
    def debug(cls, message):
        """Log a debug message"""
        cls.log(message, 'debug')