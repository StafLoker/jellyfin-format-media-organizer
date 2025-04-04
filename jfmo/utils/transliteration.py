#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Transliteration module for JFMO
"""

from ..config import Config
from .colors import Colors
from .logger import Logger

try:
    import transliterate
except ImportError:
    print("Error: Required package 'transliterate' not found.")
    print("Please install it using: pip install transliterate")
    import sys
    sys.exit(1)


class Transliterator:
    """Class for handling transliteration of texts between writing systems"""
    
    @staticmethod
    def detect_language(text):
        """Detect the language of a transliterated text"""
        for lang in Config.TRANSLITERATION_LANGS:
            if transliterate.detect_language(text, lang):
                return lang
        return None
    
    @staticmethod
    def transliterate_text(text):
        """
        Try to detect if text is transliterated from a non-Latin alphabet
        and convert it back to its original script
        """
        # Skip if text already contains non-latin characters
        if any(ord(c) > 127 for c in text):
            return text

        # Clean the text by removing unnecessary symbols
        cleaned_text = text.strip()
        
        # Common Russian transliterated words and patterns that might help in detection
        russian_indicators = [
            'podslushano', 'rybinske', 'vypusk', 'kvartirnyj', 'vopros', 
            'ot', 'tainstvennye', 'istorii', 'v', 'na', 'pri', 'dlya',
            'shch', 'zh', 'ch', 'kh', 'ya', 'yu'
        ]
        
        # Check if this might be Russian by looking for common transliterated words/patterns
        might_be_russian = any(indicator in cleaned_text.lower() for indicator in russian_indicators)
        
        # Try to detect language and transliterate
        try:
            # Try Russian first if there are indicators
            if might_be_russian:
                try:
                    translit_result = transliterate.translit(cleaned_text, 'ru', reversed=True)
                    print(f"{Colors.YELLOW}Detected Russian from indicators:{Colors.NC} {cleaned_text} -> {translit_result}")
                    Logger.info(f"Detected Russian from indicators: {cleaned_text} -> {translit_result}")
                    return translit_result
                except Exception:
                    pass
                    
            # If that fails or wasn't Russian, try all languages
            for lang in Config.TRANSLITERATION_LANGS:
                try:
                    # Check if this text can be reverse transliterated to this language
                    reverse_translit = transliterate.detect_language(cleaned_text, lang)
                    if reverse_translit:
                        # Confirm it's not just a coincidental match with a few letters
                        if len(cleaned_text) > 3:  # More than 3 chars
                            translit_result = transliterate.translit(cleaned_text, lang, reversed=True)
                            print(f"{Colors.YELLOW}Transliterated from '{lang}':{Colors.NC} {cleaned_text} -> {translit_result}")
                            Logger.info(f"Transliterated from '{lang}': {cleaned_text} -> {translit_result}")
                            return translit_result
                except Exception:
                    continue
        except Exception as e:
            print(f"{Colors.RED}Error in transliteration: {str(e)}{Colors.NC}")
            Logger.error(f"Error in transliteration: {str(e)}")
        
        return text