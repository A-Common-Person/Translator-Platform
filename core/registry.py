"""Registro de plugins. Agregar un formato nuevo no requiere tocar código existente."""

from core.parser_interface import ContentParser

PARSERS: dict[str, type[ContentParser]] = {}


def register_parser(extension: str):
    def decorator(cls):
        PARSERS[extension] = cls
        return cls
    return decorator


def get_parser(extension: str) -> ContentParser:
    extension = extension.lstrip(".")
    if extension not in PARSERS:
        raise ValueError(f"No hay parser registrado para la extensión '{extension}'")
    return PARSERS[extension]()