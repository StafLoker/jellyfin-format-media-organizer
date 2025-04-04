#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utilities module for JFMO
"""

from .colors import Colors
from .logger import Logger
from .file_ops import FileOps
from .transliteration import Transliterator

# Initialize logger
Logger.setup()
