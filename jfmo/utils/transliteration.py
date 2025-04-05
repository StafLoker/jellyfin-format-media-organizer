#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Transliteration module for JFMO
"""

import os
import re
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
        # We only support Russian transliteration
        return 'ru' if Transliterator.is_possibly_russian(text) else None
    
    @staticmethod
    def is_possibly_russian(name):
        """
        Determine if a filename is possibly a transliteration from Russian
        using advanced linguistic heuristics
        
        Args:
            name (str): Filename or text to analyze
            
        Returns:
            bool: True if possibly Russian, False otherwise
        """
        # Normalize
        name = name.lower().replace('_', '.')
        name = os.path.splitext(name)[0]  # Remove extension
        words = re.split(r'\W+', name)  # Split by non-alphanumeric separators
        
        # 1. Russian functional words in transliteration
        russian_prepositions = {'v', 'vo', 'na', 'za', 'ot', 'do', 's', 'so', 'iz', 'po', 'o', 'ob', 
                              'nad', 'pod', 'pered', 'pri', 'pro', 'bez'}
        if any(word in russian_prepositions for word in words):
            return True
            
        # 2. Detect common Russian phonetic patterns
        phonetic_patterns = ['zh', 'shch', 'kh', 'ts', 'ya', 'yu', 'ye', 'yo', 'iy', 'yy']
        if any(pat in name for pat in phonetic_patterns):
            return True
            
        # 3. Number of long words or words with double consonants
        if sum(1 for p in words if len(p) >= 8) >= 2:
            return True
            
        # 4. Letters uncommon in English but common in Russian transliterations
        suspicious_letters = set('zhchshyaeyo')  # translit-friendly
        rarity = sum(1 for c in name if c in suspicious_letters)
        if rarity / (len(name) + 1) > 0.05:
            return True
            
        # 5. File names with structure that doesn't match normal English
        if re.search(r'\b(v|ot|vypusk|seriya|serii)\b', name):
            return True
            
        # 6. Common Russian words found in file names
        russian_words = {'podslushano', 'istorii', 'vypusk', 'kvartirnyj', 'vopros', 'gorod', 
                        'chelovek', 'mashina', 'vremya', 'novye', 'novyj', 'tainstvennye', 'rybinske'}
        if any(word in russian_words for word in words):
            return True
            
        # 7. More than 40% of words end with -yj, -ij, -aya, -oe, etc.
        russian_endings = ['yj', 'ij', 'aya', 'oye', 'oe', 'ye', 'ogo', 'ego', 'ikh', 'ykh']
        russian_words_count = sum(1 for p in words if any(p.endswith(t) for t in russian_endings))
        if russian_words_count > 0 and russian_words_count / len(words) >= 0.3:
            return True
            
        # By default, we don't consider it Russian
        return False
    
    @staticmethod
    def transliterate_text(text):
        """
        Try to detect if text is transliterated from Russian
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
        
        # Check if the text is possibly Russian
        if Transliterator.is_possibly_russian(cleaned_text):
            try:
                translit_result = transliterate.translit(cleaned_text, 'ru', reversed=True)
                # Check if transliteration actually changed something substantial
                if translit_result != cleaned_text:
                    print(f"{Colors.YELLOW}Transliterated from Russian:{Colors.NC} {cleaned_text} → {translit_result}")
                    Logger.info(f"Transliterated from Russian: {cleaned_text} → {translit_result}")
                    return translit_result
            except Exception as e:
                print(f"{Colors.RED}Error in transliteration: {str(e)}{Colors.NC}")
                Logger.error(f"Error in transliteration: {str(e)}")
        
        return text