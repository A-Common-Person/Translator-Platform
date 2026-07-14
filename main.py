"""Demo end-to-end: parsear un .txt, 'traducir' cada unidad, exportar el resultado."""

import parsers.txt_parser  # noqa: F401  (necesario para que el decorator se registre)
from core.registry import get_parser
from core.models import UnitStatus
from providers.mock_provider import MockProvider


def translate_file(input_path: str, output_path: str, source_lang: str, target_lang: str):
    extension = input_path.rsplit(".", 1)[-1]
    parser = get_parser(extension)
    provider = MockProvider()

    units = parser.parse(input_path)
    print(f"Se encontraron {len(units)} unidades traducibles.")

    for unit in units:
        unit.translated_text = provider.translate(unit.source_text, source_lang, target_lang, context=unit.context)
        unit.status = UnitStatus.MACHINE_TRANSLATED

    parser.export(units, input_path, output_path)
    print(f"Traducción exportada a: {output_path}")
    return units


if __name__ == "__main__":
    translate_file("sample.txt", "sample_translated.txt", source_lang="es", target_lang="en")