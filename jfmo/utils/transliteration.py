#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Transliteration module for JFMO
"""

import os
import re
import math
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
        using linguistic patterns and statistical analysis.
        
        Args:
            name (str): Filename or text to analyze
            
        Returns:
            bool: True if possibly Russian, False otherwise
        """
        # Normalize
        original_name = name  # Save original version for case analysis
        name = name.lower().replace('_', ' ')
        name = os.path.splitext(name)[0]  # Remove extension
        words = re.split(r'\W+', name)  # Split by non-alphanumeric separators
        
        # Quick check for absolute keywords (no scoring)
        definitely_russian = {'brat', 'stalker', 'solaris', 'leviafan', 'brigada', 'admiral', 
                            'gogol', 'voyna', 'mir', 'idi i smotri', 'dobry den'}
        
        definitely_not_russian = {'the', 'shawshank', 'stranger things', 'schindler', 'fight club',
                                'private ryan', 'country for old men', 'whiplash', 'pan labyrinth',
                                'oldboy', 'rocky', 'k-19'}
        
        # Quick keyword check
        if any(r in name.lower() for r in definitely_russian):
            return True
        if any(r in name.lower() for r in definitely_not_russian):
            return False
        
        # 'i' conjunction analysis
        if ' i ' in ' ' + name.lower() + ' ' and len(words) >= 2:
            return True  # The 'i' conjunction (and) in Russian is very distinctive in titles
        
        # === DETAILED LINGUISTIC ANALYSIS ===
        
        # 1. Evaluation of distinctive Russian phonetic patterns (high specificity)
        key_russian_patterns = [
            (r'shch', 4),           # щ -> shch (very specific to Russian)
            (r'zh', 3),             # ж -> zh
            (r'kh', 3),             # х -> kh
            (r'(?<![ceisz])ts', 3), # ц -> ts (but not in words like "facts")
            (r'(?<!\w)iy\b', 3),    # "iy" common ending
            (r'(?<!\w)yy\b', 3),    # "yy" common ending
            (r'[^aeiou]yo', 2),     # ё -> yo
            (r'[^aeiou]ye', 2),     # е -> ye
            (r'[^aeiou]yu', 2),     # ю -> yu
            (r'[^aeiou]ya', 2),     # я -> ya
            (r'(?<=[szc])h(?=[^aeiouy]|$)', 1),  # sh/ch + consonant (specific)
        ]
        
        # 2. Evaluation of Russian word endings (morphology)
        russian_endings = [
            (r'(?<=[^aeiou])ov\b', 3),    # "ov" ending (Ivanov)
            (r'(?<=[^aeiou])ev\b', 3),    # "ev" ending (Medvedev)
            (r'(?<=[^aeiou])sky\b', 3),   # "sky" ending
            (r'(?<=[^aeiou])ski\b', 3),   # "ski" ending
            (r'(?<=[^aeiou])skiy\b', 3),  # "skiy" ending
            (r'(?<=[^aeiou])aya\b', 3),   # "aya" ending (feminine)
            (r'(?<=[^aeiou])oye\b', 3),   # "oye" ending (neuter)
            (r'(?<=[^aeiou])iy\b', 2),    # "iy" ending (adjective)
            (r'(?<=[^aeiou])in\b', 2),    # "in" ending (Pushkin)
            (r'(?<=\w)vich\b', 4),        # "vich" ending (patronymic)
            (r'(?<=\w)enko\b', 4),        # "enko" ending (Ukrainian/Russian)
            (r'(?<=\w)chuk\b', 4),        # "chuk" ending
        ]
        
        # 3. Evaluation of short Russian words
        short_russian_words = [
            (r'(?<!\w)i(?!\w)', 3),     # i (and) as standalone word
            (r'(?<!\w)v(?!\w)', 3),     # v (in) as preposition
            (r'(?<!\w)na(?!\w)', 2),    # na (on/at)
            (r'(?<!\w)po(?!\w)', 2),    # po (by/along)
            (r'(?<!\w)iz(?!\w)', 2),    # iz (from)
            (r'(?<!\w)do(?!\w)', 1),    # do (until)
            (r'(?<!\w)za(?!\w)', 1),    # za (behind)
            (r'(?<!\w)ot(?!\w)', 1),    # ot (from)
        ]
        
        # Evaluation of semantically Russian words (common roots)
        russian_roots = [
            (r'moskov', 4),     # Moscow
            (r'russ?k', 4),     # Russian
            (r'soviet', 4),     # Soviet
            (r'spassk', 4),     # savior
            (r'lyub', 3),       # love
            (r'gorod', 3),      # city
            (r'glav', 3),       # main
            (r'prav', 3),       # truth/right
            (r'krasn', 3),      # red/beautiful
            (r'velik', 3),      # great
            (r'dobr', 3),       # good
            (r'svidan', 3),     # goodbye
            (r'zdorov', 3),     # health
            (r'drug', 2),       # friend
            (r'noch', 2),       # night
            (r'den', 2),        # day
        ]
        
        # Calculate scores for each category
        phonetic_score = sum(weight for pattern, weight in key_russian_patterns 
                            if re.search(pattern, name))
        
        ending_score = sum(weight for pattern, weight in russian_endings 
                        if any(re.search(pattern, word) for word in words))
        
        short_word_score = sum(weight for pattern, weight in short_russian_words 
                            if re.search(pattern, ' ' + name + ' '))
        
        root_score = sum(weight for pattern, weight in russian_roots 
                        if re.search(pattern, name))
        
        # Structural characteristics of transliterated Russian
        structural_score = 0
        
        # Multiple consecutive consonants (Russian characteristic)
        if re.search(r'[bcdfghjklmnpqrstvwxz]{3,}', name):
            structural_score += 1
        
        # Words ending in consonant + y (common in Russian adjectives)
        if any(re.search(r'[bcdfghjklmnpqrstvwxz]y$', word) for word in words):
            structural_score += 2
        
        # Analysis of Russian-specific vowel patterns
        vowel_patterns = [
            (r'(?<=[^aeiou])y(?=[aeiou])', 2),  # consonant + y + vowel
            (r'(?<=[aeiou])y(?=[^aeiou]|$)', 1)  # vowel + y + consonant
        ]
        
        vowel_score = sum(weight for pattern, weight in vowel_patterns 
                        if re.search(pattern, name))
        
        # Penalties for anti-Russian features
        english_patterns = [
            r'the\s', r'\sof\s', r'\sand\s', r'\sin\s',    # English articles and prepositions
            r'ing\b', r'ed\b', r'ment\b', r'ness\b',      # Common English suffixes
            r'[^aeiou]th', r'wh', r'qu', r'(?<![cs])k(?!h)'  # Typically English letter combinations
        ]
        
        english_penalty = sum(1 for pattern in english_patterns 
                            if re.search(pattern, ' ' + name + ' '))
        
        # Calculate total score adjusted by length
        total_score = (phonetic_score * 1.5) + ending_score + (short_word_score * 1.2) + root_score + structural_score + vowel_score - (english_penalty * 2)
        
        # Normalization for short vs long texts
        word_count = len(words)
        char_count = len(name)
        
        if word_count <= 1:
            # For a single word, we need stronger evidence
            threshold = 3.0
            if char_count <= 5:  # Very short words need stronger signals
                threshold = 4.0
        elif word_count == 2:
            threshold = 2.5
        else:
            threshold = 2.0  # For longer phrases, we can be more flexible
        
        # Special case for clearly identifiable Russian proper names
        if any(re.search(r'\b[A-Z][a-z]*(?:ov|ev|in|sky|ski)\b', original_name) for word in original_name.split()):
            return True
        
        # Special cases for conjunctions and short Russian words in an appropriate context
        if ' i ' in ' ' + name + ' ' and not any(eng_word in name for eng_word in ['with', 'the', 'and', 'of']):
            total_score += 2
        
        return total_score >= threshold
    
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
                translit_result = transliterate.translit(cleaned_text, 'ru')
                # Check if transliteration actually changed something substantial
                if translit_result != cleaned_text:
                    print(f"{Colors.YELLOW}Transliterated from Russian:{Colors.NC} {cleaned_text} → {translit_result}")
                    Logger.info(f"Transliterated from Russian: {cleaned_text} → {translit_result}")
                    return translit_result
            except Exception as e:
                print(f"{Colors.RED}Error in transliteration: {str(e)}{Colors.NC}")
                Logger.error(f"Error in transliteration: {str(e)}")
        
        return text