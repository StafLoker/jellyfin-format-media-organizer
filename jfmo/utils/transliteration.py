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

        # Skip if text is empty
        if not text.strip():
            return text
            
        # Clean the text by removing unnecessary symbols
        cleaned_text = text.strip()
        
        # Specific transliterated Russian indicators
        russian_indicators = [
            'podslushano', 'rybinske', 'vypusk', 'kvartirnyj', 'vopros', 
            'tainstvennye', 'istorii'
        ]
        
        # Common English words that should NOT be considered as indicators
        english_common = [
            'the', 'and', 'doctor', 'who', 'christmas', 'special', 'episode',
            'season', 'part', 'show', 'series', 'movie', 'film', 'documentary',
            'avatar', 'friends', 'house', 'game', 'breaking', 'bad', 'severance',
            'succession', 'loki', 'mandalorian', 'stranger', 'things', 'daily'
        ]
        
        # Check if the text contains common English words
        words = cleaned_text.lower().split()
        
        # If no words, return the original text
        if not words:
            return text
            
        common_english_word_count = sum(1 for word in words if word in english_common)
        
        # If there are many common English words, it's not Russian
        if common_english_word_count > 0 and common_english_word_count / len(words) > 0.2:
            return text
        
        # Check for specific Russian indicators
        specific_russian_indicators = [word for word in words if word in russian_indicators]
        might_be_russian = len(specific_russian_indicators) > 0
        
        # Try to detect language and transliterate
        try:
            # Try Russian first if there are indicators
            if might_be_russian:
                try:
                    translit_result = transliterate.translit(cleaned_text, 'ru', reversed=True)
                    # Check if transliteration actually changed something substantial
                    if translit_result != cleaned_text:
                        print(f"{Colors.YELLOW}Transliterated from Russian:{Colors.NC} {cleaned_text} → {translit_result}")
                        Logger.info(f"Transliterated from Russian: {cleaned_text} → {translit_result}")
                        return translit_result
                except Exception:
                    pass
                    
            # If not Russian but title doesn't seem English (few English indicators), try other languages
            if common_english_word_count / len(words) < 0.2:
                for lang in Config.TRANSLITERATION_LANGS:
                    if lang == 'ru':  # Already tried Russian
                        continue
                    try:
                        # Check if this text can be reverse transliterated to this language
                        reverse_translit = transliterate.detect_language(cleaned_text, lang)
                        if reverse_translit:
                            # Confirm it's not just a coincidental match with a few letters
                            if len(cleaned_text) > 3:  # More than 3 chars
                                try:
                                    translit_result = transliterate.translit(cleaned_text, lang, reversed=True)
                                    if translit_result != cleaned_text:  # Only if there's a real change
                                        print(f"{Colors.YELLOW}Transliterated from '{lang}':{Colors.NC} {cleaned_text} → {translit_result}")
                                        Logger.info(f"Transliterated from '{lang}': {cleaned_text} → {translit_result}")
                                        return translit_result
                                except:
                                    continue
                    except Exception:
                        continue
        except Exception as e:
            print(f"{Colors.RED}Error in transliteration: {str(e)}{Colors.NC}")
            Logger.error(f"Error in transliteration: {str(e)}")
        
        return text