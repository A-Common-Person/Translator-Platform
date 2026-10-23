"""Carpetas del proyecto. Se asume que los comandos se corren desde la raíz del repositorio."""

from pathlib import Path

SAMPLES_DIR = Path("samples")    # archivos de entrada de ejemplo
OUTPUT_DIR = Path("output")      # archivos traducidos y exportados
PROJECTS_DIR = Path("projects")  # proyectos de revisión (.json)
DATA_DIR = Path("data")          # memoria de traducción y otros datos locales

for _folder in (SAMPLES_DIR, OUTPUT_DIR, PROJECTS_DIR, DATA_DIR):
    _folder.mkdir(exist_ok=True)


def in_folder(folder: Path, path: str) -> str:
    """Si `path` es solo un nombre de archivo, lo coloca dentro de `folder`.
    Si ya incluye una carpeta, se respeta tal cual."""
    p = Path(path)
    if p.parent == Path("."):
        return (folder / p.name).as_posix()
    return p.as_posix()