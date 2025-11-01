#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Transliteration module for JFMO - Using trained N-gram models
"""

import os
import pickle
from pathlib import Path
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


class NgramLanguageDetector:
    """N-gram based language detector for Russian/English classification"""
    
    def __init__(self, model_ru_path, model_en_path):
        with open(model_ru_path, 'rb') as f:
            self.model_ru = pickle.load(f)
        with open(model_en_path, 'rb') as f:
            self.model_en = pickle.load(f)
    
    def detect(self, text, min_confidence=0.0):
        """
        Detect language using trained models
        
        Returns:
            tuple: (language, confidence, is_certain)
        """
        if not text or len(text.strip()) < 2:
            return 'unknown', 0.0, False
        
        text = text.strip()
        prob_ru = self.model_ru.probability(text)
        prob_en = self.model_en.probability(text)
        
        confidence = abs(prob_ru - prob_en)
        is_certain = confidence >= min_confidence
        
        language = 'ru' if prob_ru > prob_en else 'en'
        
        if not is_certain:
            language = 'unknown'
        
        return language, confidence, is_certain


class Transliterator:
    """Class for handling transliteration using trained models"""
    
    _detector = None
    
    @classmethod
    def _get_detector(cls):
        if cls._detector is None:
            current_dir = Path(__file__).parent.parent.parent
            model_ru_path = current_dir / "models" / "jfmo_russian_model.pkl"
            model_en_path = current_dir / "models" / "jfmo_english_model.pkl"
            
            cls._detector = NgramLanguageDetector(str(model_ru_path), str(model_en_path))
            Logger.info("N-gram language detector initialized")
        
        return cls._detector
    
    @staticmethod
    def detect_language(text):
        """Detect if text is Russian"""
        detector = Transliterator._get_detector()
        language, _ , _ = detector.detect(text, min_confidence=0.0)
        return 'ru' if language == 'ru' else None
    
    @staticmethod
    def is_possibly_russian(name):
        """Check if text is possibly Russian using trained models"""
        name = name.lower().replace('_', ' ')
        name = os.path.splitext(name)[0]
        
        detector = Transliterator._get_detector()
        language, _, _ = detector.detect(name, min_confidence=0.0)
        
        return language == 'ru'
    
    @staticmethod
    def transliterate_text(text):
        """Transliterate Russian text back to Cyrillic"""
        if any(ord(c) > 127 for c in text):
            return text

        if not text.strip():
            return text
        
        cleaned_text = text.strip()
        
        if Transliterator.is_possibly_russian(cleaned_text):
            try:
                translit_result = transliterate.translit(cleaned_text, 'ru')
                
                if translit_result != cleaned_text:
                    print(f"{Colors.YELLOW}Transliterated from Russian:{Colors.NC} {cleaned_text} → {translit_result}")
                    Logger.info(f"Transliterated from Russian: {cleaned_text} → {translit_result}")
                    return translit_result
            except Exception as e:
                print(f"{Colors.RED}Error in transliteration: {str(e)}{Colors.NC}")
                Logger.error(f"Error in transliteration: {str(e)}")
        
        return text