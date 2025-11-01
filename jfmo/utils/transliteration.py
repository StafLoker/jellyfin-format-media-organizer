import os
import pickle
import math
from pathlib import Path
from collections import defaultdict, Counter
from .colors import Colors
from .logger import Logger

try:
    import transliterate
except ImportError:
    print("Error: Required package 'transliterate' not found.")
    print("Please install it using: pip install transliterate")
    import sys
    sys.exit(1)


class NgramModel:
    """N-gram language model for text classification"""
    
    def __init__(self, n=3):
        self.n = n
        self.ngrams = defaultdict(Counter)
    
    def probability(self, text):
        """Calculate log probability of text"""
        text = text.lower() + ' '
        log_prob = 0.0
        
        for i in range(len(text) - self.n):
            context = text[i:i+self.n]
            next_char = text[i+self.n]
            
            count_next = self.ngrams[context][next_char]
            count_total = sum(self.ngrams[context].values())
            
            if count_total > 0:
                prob = (count_next + 1) / (count_total + 100)
                log_prob += math.log(prob)
            else:
                log_prob += math.log(0.001)
        
        return log_prob / len(text) if len(text) > 0 else -1000
    
    @staticmethod
    def load(filepath):
        """Load model from file"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        model = NgramModel(n=data['n'])
        model.ngrams = defaultdict(Counter, data['ngrams'])
        
        return model


class NgramLanguageDetector:
    """N-gram based language detector for Russian/English classification"""
    
    def __init__(self, model_ru_path, model_en_path):
        """Load and validate models"""
        try:
            # Load models using the load method
            self.model_ru = NgramModel.load(model_ru_path)
            self.model_en = NgramModel.load(model_en_path)
            
            # Test models
            test_text = "test"
            self.model_ru.probability(test_text)
            self.model_en.probability(test_text)
            
            Logger.info("Language models loaded and validated successfully")
            
        except Exception as e:
            Logger.error(f"Failed to load models: {e}")
            raise
    
    def detect(self, text, min_confidence=0.0):
        """Detect language using trained models"""
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
            try:
                current_dir = Path(__file__).parent.parent.parent
                model_ru_path = current_dir / "models" / "jfmo_russian_model.pkl"
                model_en_path = current_dir / "models" / "jfmo_english_model.pkl"
                
                cls._detector = NgramLanguageDetector(str(model_ru_path), str(model_en_path))
                Logger.info("N-gram language detector initialized")
            except Exception as e:
                Logger.warning(f"Failed to load language models: {str(e)}")
                Logger.warning("Falling back to basic Russian character detection")
                cls._detector = None
        
        return cls._detector
    
    @staticmethod
    def detect_language(text):
        """Detect if text is Russian"""
        detector = Transliterator._get_detector()
        
        if detector is None:
            # Fallback: check for Cyrillic characters
            if any('\u0400' <= c <= '\u04FF' for c in text):
                return 'ru'
            return None
        
        language, _, _ = detector.detect(text, min_confidence=0.0)
        return 'ru' if language == 'ru' else None
    
    @staticmethod
    def is_possibly_russian(name):
        """Check if text is possibly Russian using trained models"""
        name = name.lower().replace('_', ' ')
        name = os.path.splitext(name)[0]
        
        detector = Transliterator._get_detector()
        
        if detector is None:
            # Fallback: check for Cyrillic characters
            return any('\u0400' <= c <= '\u04FF' for c in name)
        
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