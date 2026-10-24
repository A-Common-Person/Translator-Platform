"""Limpia saltos de línea y espacios repetidos en un proyecto ya creado (útil para EPUB antiguos).

Uso: python clean_project.py <proyecto.json>
Guarda una copia de seguridad como <proyecto.json>.bak antes de modificar nada.
"""

import shutil
import sys

from core.paths import PROJECTS_DIR, in_folder
from core.project_store import ProjectStore


def clean(text):
    return " ".join(text.split()) if text else text


def clean_project(project_path: str):
    project_path = in_folder(PROJECTS_DIR, project_path)
    shutil.copy(project_path, project_path + ".bak")

    project = ProjectStore.load(project_path)
    changed = 0
    for unit in project.units:
        new_source = clean(unit.source_text)
        new_translation = clean(unit.translated_text)
        if new_source != unit.source_text or new_translation != unit.translated_text:
            changed += 1
        unit.source_text = new_source
        unit.translated_text = new_translation

    ProjectStore.save(project, project_path)
    print(f"{changed} de {len(project.units)} unidades limpiadas en {project_path}")
    print(f"Copia de seguridad: {project_path}.bak")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python clean_project.py <proyecto.json>")
        sys.exit(1)
    clean_project(sys.argv[1])