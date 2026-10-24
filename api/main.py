"""API local para el editor de revisión. Corre en tu propia máquina, sin servidor externo."""

import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.paths import PROJECTS_DIR, OUTPUT_DIR
from core.project_store import ProjectStore
from core.models import UnitStatus
from core.translation_memory import TranslationMemory
from core.registry import get_parser
from parsers.txt_parser import TxtParser  # noqa: F401
from parsers.epub_parser import EpubParser  # noqa: F401

app = FastAPI()

# Permite que la página web (que corre en otro puerto) le hable a esta API sin que el navegador la bloquee
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class UnitUpdate(BaseModel):
    translated_text: str


def project_file(name: str) -> str:
    """Convierte el nombre de un proyecto en su ruta, validando que no pueda salirse de projects/."""
    if not re.fullmatch(r"[\w\- ]+", name):
        raise HTTPException(status_code=400, detail="Nombre de proyecto inválido")
    path = PROJECTS_DIR / f"{name}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return path.as_posix()


@app.get("/projects")
def list_projects():
    items = []
    for path in sorted(PROJECTS_DIR.glob("*.json")):
        try:
            project = ProjectStore.load(path.as_posix())
        except Exception:
            continue  # ignora archivos .json que no sean proyectos válidos
        approved = sum(1 for u in project.units if u.status == UnitStatus.APPROVED)
        items.append({"name": path.stem, "approved": approved, "total": len(project.units)})
    return items


@app.get("/projects/{name}")
def get_project(name: str):
    project = ProjectStore.load(project_file(name))
    return project.model_dump()


@app.post("/projects/{name}/units/{unit_id}")
def update_unit(name: str, unit_id: str, update: UnitUpdate):
    path = project_file(name)
    project = ProjectStore.load(path)
    unit = next((u for u in project.units if u.id == unit_id), None)
    if not unit:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")

    unit.translated_text = update.translated_text
    unit.status = UnitStatus.APPROVED

    memory = TranslationMemory()
    memory.store(unit.source_text, unit.translated_text, project.source_lang, project.target_lang)

    ProjectStore.save(project, path)
    return unit.model_dump()


@app.post("/projects/{name}/export")
def export_project(name: str):
    project = ProjectStore.load(project_file(name))
    extension = project.original_path.rsplit(".", 1)[-1]
    parser = get_parser(extension)

    output_path = (OUTPUT_DIR / f"{name}_translated.{extension}").as_posix()
    parser.export(project.units, project.original_path, output_path)

    return {"output_path": output_path}