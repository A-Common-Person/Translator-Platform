"""Etapa 3: exportar un proyecto ya revisado al archivo final."""

import sys
import parsers.txt_parser  # noqa: F401
import parsers.epub_parser  # noqa: F401
from core.paths import PROJECTS_DIR, OUTPUT_DIR, in_folder
from core.registry import get_parser
from core.project_store import ProjectStore


def export_project(project_path: str, output_path: str):
    # Un nombre suelto se busca en projects/ y el resultado se guarda en output/
    project_path = in_folder(PROJECTS_DIR, project_path)
    output_path = in_folder(OUTPUT_DIR, output_path)

    project = ProjectStore.load(project_path)
    extension = project.original_path.rsplit(".", 1)[-1]
    parser = get_parser(extension)
    parser.export(project.units, project.original_path, output_path)
    print(f"Exportado a: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python export_project.py <proyecto.json> <archivo_salida>")
        sys.exit(1)
    export_project(sys.argv[1], sys.argv[2])