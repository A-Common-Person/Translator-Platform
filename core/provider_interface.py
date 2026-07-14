"""Todo proveedor de traducción (Claude, DeepL, Google, mock) implementa esta interfaz."""

from abc import ABC, abstractmethod


class TranslationProvider(ABC):
    @abstractmethod
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str | None = None,
        glossary: dict[str, str] | None = None,
    ) -> str:
        ...