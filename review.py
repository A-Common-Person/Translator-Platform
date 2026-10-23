"""Etapa 2: revisar y corregir traducciones antes de exportar."""

import sys
from core.paths import PROJECTS_DIR, in_folder
from core.project_store import ProjectStore
from core.models import UnitStatus
from core.translation_memory import TranslationMemory


def review(project_path: str):
    project_path = in_folder(PROJECTS_DIR, project_path)
    project = ProjectStore.load(project_path)
    memory = TranslationMemory()

    pending = [u for u in project.units if u.status != UnitStatus.APPROVED]
    print(f"{len(pending)} unidades pendientes de revisión de {len(project.units)} totales.\n")

    for i, unit in enumerate(pending):
        print(f"--- Unidad {i + 1}/{len(pending)} ---")
        print(f"Original:   {unit.source_text}")
        print(f"Traducción: {unit.translated_text}")
        choice = input("[Enter]=aprobar  [texto nuevo]=corregir  [s]=saltar  [q]=guardar y salir: ").strip()

        if choice.lower() == "q":
            break
        elif choice.lower() == "s":
            continue
        elif choice == "":
            unit.status = UnitStatus.APPROVED
        else:
            unit.translated_text = choice
            unit.status = UnitStatus.APPROVED
            memory.store(unit.source_text, unit.translated_text, project.source_lang, project.target_lang)
        print()

    ProjectStore.save(project, project_path)
    approved_count = sum(1 for u in project.units if u.status == UnitStatus.APPROVED)
    print(f"\nGuardado. {approved_count}/{len(project.units)} unidades aprobadas.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python review.py <proyecto.json>")
        sys.exit(1)
    review(sys.argv[1])