"""Parser de archivos EPUB. Extrae párrafos de cada capítulo como unidades traducibles."""

from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup

from core.parser_interface import ContentParser
from core.models import TranslatableUnit
from core.registry import register_parser


@register_parser("epub")
class EpubParser(ContentParser):
    def parse(self, file_path: str) -> list[TranslatableUnit]:
        book = epub.read_epub(file_path)
        units = []
        unit_index = 0

        for item in book.get_items_of_type(ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), "html.parser")
            paragraphs = soup.find_all(["p", "h1", "h2", "h3"])

            for p_index, tag in enumerate(paragraphs):
                # Dentro de un párrafo de EPUB, los saltos de línea son solo formato del archivo:
                # se juntan en un único espacio para que el texto quede continuo.
                text = " ".join(tag.get_text().split())
                if not text:
                    continue
                units.append(
                    TranslatableUnit(
                        id=f"unit-{unit_index}",
                        source_text=text,
                        metadata={"item_id": item.get_id(), "paragraph_index": p_index},
                    )
                )
                unit_index += 1

        return units

    def export(self, units: list[TranslatableUnit], original_path: str, output_path: str) -> None:
        book = epub.read_epub(original_path)

        units_by_item: dict[str, dict[int, TranslatableUnit]] = {}
        for unit in units:
            item_id = unit.metadata["item_id"]
            p_index = unit.metadata["paragraph_index"]
            units_by_item.setdefault(item_id, {})[p_index] = unit

        for item in book.get_items_of_type(ITEM_DOCUMENT):
            if item.get_id() not in units_by_item:
                continue

            soup = BeautifulSoup(item.get_content(), "html.parser")
            paragraphs = soup.find_all(["p", "h1", "h2", "h3"])
            item_units = units_by_item[item.get_id()]

            for p_index, tag in enumerate(paragraphs):
                unit = item_units.get(p_index)
                if unit and unit.translated_text:
                    tag.string = unit.translated_text

            item.set_content(str(soup).encode("utf-8"))

        book.toc = []  # evita el error de NCX; reconstruir la tabla de contenidos queda pendiente
        epub.write_epub(output_path, book)