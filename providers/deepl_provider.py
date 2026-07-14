"""Proveedor de traducción real usando la API gratuita de DeepL."""

import os
import deepl
from dotenv import load_dotenv
from core.provider_interface import TranslationProvider

load_dotenv()


class DeepLProvider(TranslationProvider):
    def __init__(self):
        api_key = os.getenv("DEEPL_API_KEY")
        if not api_key:
            raise ValueError("No se encontró DEEPL_API_KEY en el archivo .env")
        self.client = deepl.Translator(api_key)

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str | None = None,
        glossary: dict[str, str] | None = None,
    ) -> str:
        result = self.client.translate_text(
            text,
            source_lang=source_lang.upper(),
            target_lang=self._normalize_target(target_lang),
        )
        return result.text

    @staticmethod
    def _normalize_target(target_lang: str) -> str:
        # DeepL exige variantes regionales para algunos idiomas (ej: EN-US en vez de EN)
        mapping = {"en": "EN-US", "pt": "PT-PT"}
        return mapping.get(target_lang.lower(), target_lang.upper())