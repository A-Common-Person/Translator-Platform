"""Proveedor de traducción real usando la API gratuita de DeepL, con soporte de glosario."""

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
        self._glossary_cache: dict[str, object] = {}  # "es-en" -> objeto glosario de DeepL

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str | None = None,
        glossary: dict[str, str] | None = None,
    ) -> str:
        target = self._normalize_target(target_lang)
        glossary_obj = None
        if glossary:
            glossary_obj = self._get_or_create_glossary(glossary, source_lang, target)

        result = self.client.translate_text(
            text,
            source_lang=source_lang.upper(),
            target_lang=target,
            glossary=glossary_obj,
        )
        return result.text

    def _get_or_create_glossary(self, glossary_dict: dict[str, str], source_lang: str, target_lang: str):
        cache_key = f"{source_lang}-{target_lang}"
        if cache_key in self._glossary_cache:
            return self._glossary_cache[cache_key]

        glossary_name = f"translator-platform-{cache_key}"

        # Reutiliza el glosario si ya existe de una corrida anterior, en vez de duplicarlo
        for existing in self.client.list_glossaries():
            if existing.name == glossary_name:
                self._glossary_cache[cache_key] = existing
                return existing

        new_glossary = self.client.create_glossary(
            glossary_name,
            source_lang=source_lang.upper(),
            target_lang=target_lang,
            entries=glossary_dict,
        )
        self._glossary_cache[cache_key] = new_glossary
        return new_glossary

    @staticmethod
    def _normalize_target(target_lang: str) -> str:
        mapping = {"en": "EN-US", "pt": "PT-PT"}
        return mapping.get(target_lang.lower(), target_lang.upper())