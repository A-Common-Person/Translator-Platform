"""Demo end-to-end: parsear un .txt, traducir con glosario + memoria, exportar el resultado."""

import parsers.txt_parser  # noqa: F401
from core.registry import get_parser
from core.models import UnitStatus
from core.translation_memory import TranslationMemory
from providers.deepl_provider import DeepLProvider


def translate_file(input_path, output_path, source_lang, target_lang, glossary=None):
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
            print(f"  (desde memoria) {unit.source_text!r}")
        else:
            unit.translated_text = provider.translate(
                unit.source_text, source_lang, target_lang, context=unit.context, glossary=glossary
            )
            memory.store(unit.source_text, unit.translated_text, source_lang, target_lang)
            print(f"  (traducido por DeepL) {unit.source_text!r}")
        unit.status = UnitStatus.MACHINE_TRANSLATED

    parser.export(units, input_path, output_path)
    print(f"Traducción exportada a: {output_path}")
    return units


if __name__ == "__main__":
    ejemplo_glosario = {"Aria": "Aria", "espada de fuego": "flame sword"}
    translate_file(
        "sample.txt", "sample_translated.txt",
        source_lang="es", target_lang="en",
        glossary=ejemplo_glosario,
    )