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
        
        # Palabras específicas rusas transliteradas - más estricto que antes
        russian_indicators = [
            'podslushano', 'rybinske', 'vypusk', 'kvartirnyj', 'vopros', 
            'tainstvennye', 'istorii'
        ]
        
        # Combinaciones de letras específicas que son comunes en ruso transliterado
        russian_patterns = [
            'shch', 'zh', 'kh', 'ts', 'ch', 'sch'
        ]
        
        # Palabras en inglés comunes que NO deben ser consideradas como indicadores
        english_common = [
            'the', 'and', 'doctor', 'who', 'christmas', 'special', 'episode',
            'season', 'part', 'show', 'series', 'movie', 'film', 'documentary',
            'avatar', 'friends', 'house', 'game', 'breaking', 'bad', 'severance',
            'succession', 'loki', 'mandalorian', 'stranger', 'things', 'daily'
        ]
        
        # Verificar si el texto contiene palabras inglesas comunes
        words = cleaned_text.lower().split()
        common_english_word_count = sum(1 for word in words if word in english_common)
        
        # Si hay muchas palabras inglesas comunes, no es ruso
        if common_english_word_count > 0 and common_english_word_count / len(words) > 0.3:
            return text
        
        # Verificar indicadores específicos de ruso
        specific_russian_indicators = [word for word in words if word in russian_indicators]
        russian_pattern_matches = [pattern for pattern in russian_patterns if pattern in cleaned_text.lower()]
        
        # Solo transliterar si hay indicadores específicos rusos
        might_be_russian = len(specific_russian_indicators) > 0 or len(russian_pattern_matches) >= 2
        
        # Try to detect language and transliterate
        try:
            # Try Russian first if there are indicators
            if might_be_russian:
                try:
                    translit_result = transliterate.translit(cleaned_text, 'ru', reversed=True)
                    # Verificar si la transliteración realmente cambió algo sustancial
                    if translit_result != cleaned_text:
                        print(f"{Colors.YELLOW}Detected Russian from indicators:{Colors.NC} {cleaned_text} -> {translit_result}")
                        Logger.info(f"Detected Russian from indicators: {cleaned_text} -> {translit_result}")
                        return translit_result
                except Exception:
                    pass
                    
            # Si no es ruso pero el título no parece inglés (pocos indicadores ingleses), probar otros idiomas
            if common_english_word_count / len(words) < 0.2:
                for lang in Config.TRANSLITERATION_LANGS:
                    if lang == 'ru':  # Ya lo intentamos con ruso
                        continue
                    try:
                        # Check if this text can be reverse transliterated to this language
                        reverse_translit = transliterate.detect_language(cleaned_text, lang)
                        if reverse_translit:
                            # Confirm it's not just a coincidental match with a few letters
                            if len(cleaned_text) > 3:  # More than 3 chars
                                translit_result = transliterate.translit(cleaned_text, lang, reversed=True)
                                if translit_result != cleaned_text:  # Solo si hay cambio real
                                    print(f"{Colors.YELLOW}Transliterated from '{lang}':{Colors.NC} {cleaned_text} -> {translit_result}")
                                    Logger.info(f"Transliterated from '{lang}': {cleaned_text} -> {translit_result}")
                                    return translit_result
                    except Exception:
                        continue
        except Exception as e:
            print(f"{Colors.RED}Error in transliteration: {str(e)}{Colors.NC}")
            Logger.error(f"Error in transliteration: {str(e)}")
        
        return text