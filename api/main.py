"""API local para el editor de revisión. Corre en tu propia máquina, sin servidor externo."""

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

PROJECT_PATH = (PROJECTS_DIR / "proyecto.json").as_posix()  # por ahora, fijo; más adelante será seleccionable

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


@app.get("/project")
def get_project():
    project = ProjectStore.load(PROJECT_PATH)
    return project.model_dump()


@app.post("/units/{unit_id}")
def update_unit(unit_id: str, update: UnitUpdate):
    project = ProjectStore.load(PROJECT_PATH)
    unit = next((u for u in project.units if u.id == unit_id), None)
    if not unit:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")

    unit.translated_text = update.translated_text
    unit.status = UnitStatus.APPROVED

    memory = TranslationMemory()
    memory.store(unit.source_text, unit.translated_text, project.source_lang, project.target_lang)

    ProjectStore.save(project, PROJECT_PATH)
    return unit.model_dump()


@app.post("/export")
def export_project():
    project = ProjectStore.load(PROJECT_PATH)
    extension = project.original_path.rsplit(".", 1)[-1]
    parser = get_parser(extension)

    output_path = (OUTPUT_DIR / f"exported.{extension}").as_posix()
    parser.export(project.units, project.original_path, output_path)

    return {"output_path": output_path}