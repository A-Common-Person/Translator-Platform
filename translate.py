"""Etapa 1: parsear un archivo y traducir todas sus unidades, guardando el proyecto para revisión."""

import sys
import parsers.txt_parser  # noqa: F401
import parsers.epub_parser  # noqa: F401
from core.registry import get_parser
from core.models import Project, UnitStatus
from core.translation_memory import TranslationMemory
from core.project_store import ProjectStore
from providers.deepl_provider import DeepLProvider


def translate_file(input_path, project_path, source_lang, target_lang, glossary=None):
    extension = input_path.rsplit(".", 1)[-1]
    parser = get_parser(extension)
    provider = DeepLProvider()
    memory = TranslationMemory()

    units = parser.parse(input_path)
    print(f"Se encontraron {len(units)} unidades traducibles.")

    for unit in units:
        cached = memory.lookup(unit.source_text, source_lang, target_lang)
        if cached:
            unit.translated_text = cached
        else:
            unit.translated_text = provider.translate(
                unit.source_text, source_lang, target_lang, context=unit.context, glossary=glossary
            )
            memory.store(unit.source_text, unit.translated_text, source_lang, target_lang)
        unit.status = UnitStatus.MACHINE_TRANSLATED

    project = Project(
        id="demo-project",
        name=input_path,
        source_lang=source_lang,
        target_lang=target_lang,
        original_path=input_path,
        units=units,
    )
    ProjectStore.save(project, project_path)
    print(f"Proyecto guardado en: {project_path} (listo para revisar)")


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Uso: python translate.py <archivo_entrada> <proyecto.json> <idioma_origen> <idioma_destino>")
        sys.exit(1)
    translate_file(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])