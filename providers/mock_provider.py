"""Proveedor falso, solo para validar que el flujo completo funciona de punta a punta."""

from core.provider_interface import TranslationProvider


class MockProvider(TranslationProvider):
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str | None = None,
        glossary: dict[str, str] | None = None,
    ) -> str:
        return f"[{target_lang.upper()}] {text}"