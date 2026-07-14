"""Parser de archivos de texto plano. Una unidad traducible por línea no vacía."""

from core.parser_interface import ContentParser
from core.models import TranslatableUnit
from core.registry import register_parser


@register_parser("txt")
class TxtParser(ContentParser):
    def parse(self, file_path: str) -> list[TranslatableUnit]:
        units = []
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                stripped = line.rstrip("\n")
                if stripped.strip() == "":
                    continue
                units.append(
                    TranslatableUnit(
                        id=f"line-{i}",
                        source_text=stripped,
                        metadata={"line_number": i},
                    )
                )
        return units

    def export(self, units: list[TranslatableUnit], original_path: str, output_path: str) -> None:
        units_by_line = {u.metadata["line_number"]: u for u in units}
        with open(original_path, "r", encoding="utf-8") as f:
            original_lines = f.readlines()

        with open(output_path, "w", encoding="utf-8") as out:
            for i, original_line in enumerate(original_lines):
                unit = units_by_line.get(i)
                if unit and unit.translated_text:
                    out.write(unit.translated_text + "\n")
                else:
                    out.write(original_line)