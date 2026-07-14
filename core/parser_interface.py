"""Todo parser de formato (TXT, EPUB, JSON de juego, OCR) implementa esta interfaz."""

from abc import ABC, abstractmethod
from core.models import TranslatableUnit


class ContentParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> list[TranslatableUnit]:
        """Convierte el archivo original en una lista de unidades traducibles."""
        ...

    @abstractmethod
    def export(self, units: list[TranslatableUnit], original_path: str, output_path: str) -> None:
        """Reconstruye el archivo original con las traducciones aplicadas."""
        ...