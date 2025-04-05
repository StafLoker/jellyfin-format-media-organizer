#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Terminal colors utility for JFMO
"""


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color
    
    @classmethod
    def green(cls, text):
        """Format text with green color"""
        return f"{cls.GREEN}{text}{cls.NC}"
    
    @classmethod
    def yellow(cls, text):
        """Format text with yellow color"""
        return f"{cls.YELLOW}{text}{cls.NC}"
    
    @classmethod
    def blue(cls, text):
        """Format text with blue color"""
        return f"{cls.BLUE}{text}{cls.NC}"
    
    @classmethod
    def red(cls, text):
        """Format text with red color"""
        return f"{cls.RED}{text}{cls.NC}"