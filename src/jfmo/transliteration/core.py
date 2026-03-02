import math
import pickle
from collections import Counter, defaultdict
from importlib.resources import as_file, files

import transliterate
from loguru import logger

from ..exceptions import TransliterationModelError


class NgramModel:
    def __init__(self, n=3):
        self.n = n
        self.ngrams = defaultdict(Counter)

    def probability(self, text):
        text = text.lower() + " "
        log_prob = 0.0

        for i in range(len(text) - self.n):
            context = text[i : i + self.n]
            next_char = text[i + self.n]

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
        with open(filepath, "rb") as f:
            data = pickle.load(f)

        model = NgramModel(n=data["n"])
        model.ngrams = defaultdict(Counter, data["ngrams"])
        return model


class Transliterator:
    _model_ru: NgramModel
    _model_en: NgramModel
    _models_loaded: bool = False

    @classmethod
    def _load_models(cls) -> None:
        if cls._models_loaded:
            return

        try:
            pkg = files("jfmo.transliteration.models")
            with (
                as_file(pkg.joinpath("jfmo_russian_model.pkl")) as path_ru,
                as_file(pkg.joinpath("jfmo_english_model.pkl")) as path_en,
            ):
                cls._model_ru = NgramModel.load(path_ru)
                cls._model_en = NgramModel.load(path_en)
            cls._model_ru.probability("test")
            cls._model_en.probability("test")
            cls._models_loaded = True
            logger.info("Language models loaded and validated successfully")
        except Exception as e:
            raise TransliterationModelError(f"Failed to load language models: {e}") from e

    @classmethod
    def is_possibly_russian(cls, name: str) -> bool:
        cls._load_models()
        if not name or len(name) < 2:
            return False
        return cls._model_ru.probability(name) > cls._model_en.probability(name)

    @classmethod
    def transliterate_text(cls, text: str) -> str:
        if any(ord(c) > 127 for c in text) or not text:
            return text
        if not cls.is_possibly_russian(text):
            return text
        try:
            result = transliterate.translit(text, "ru")
            if result != text:
                logger.info(f"Transliterated: {text} → {result}")
                return result
        except Exception as e:
            logger.error(f"Transliteration error: {e}")
        return text
