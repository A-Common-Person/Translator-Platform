"""Pipeline de traducción: parsea un archivo, traduce cada unidad y guarda el proyecto para revisión."""

from pathlib import Path

import parsers.txt_parser  # noqa: F401
import parsers.epub_parser  # noqa: F401
from core.paths import SAMPLES_DIR, PROJECTS_DIR, in_folder
from core.registry import get_parser
from core.models import Project, UnitStatus
from core.translation_memory import TranslationMemory
from core.project_store import ProjectStore
from providers.deepl_provider import DeepLProvider


def translate_file(input_path, project_path, source_lang, target_lang, glossary=None, on_progress=None):
    """Traduce `input_path` y guarda el proyecto en `project_path`.

    `on_progress(hechas, total)` se llama tras cada unidad, para mostrar el avance.
    """
    # Un nombre suelto se busca en samples/ y el proyecto se guarda en projects/
    input_path = in_folder(SAMPLES_DIR, input_path)
    project_path = in_folder(PROJECTS_DIR, project_path)

    extension = input_path.rsplit(".", 1)[-1].lower()
    parser = get_parser(extension)
    provider = DeepLProvider()
    memory = TranslationMemory()

    units = parser.parse(input_path)
    total = len(units)
    print(f"Se encontraron {total} unidades traducibles.")
    if on_progress:
        on_progress(0, total)

    for done, unit in enumerate(units, start=1):
        cached = memory.lookup(unit.source_text, source_lang, target_lang)
        if cached:
            unit.translated_text = cached
        else:
            unit.translated_text = provider.translate(
                unit.source_text, source_lang, target_lang, context=unit.context, glossary=glossary
            )
            memory.store(unit.source_text, unit.translated_text, source_lang, target_lang)
        unit.status = UnitStatus.MACHINE_TRANSLATED
        if on_progress:
            on_progress(done, total)

    project = Project(
        id=Path(project_path).stem,
        name=input_path,
        source_lang=source_lang,
        target_lang=target_lang,
        original_path=input_path,
        units=units,
    )
    ProjectStore.save(project, project_path)
    print(f"Proyecto guardado en: {project_path} (listo para revisar)")
    return project_path