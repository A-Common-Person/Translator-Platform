"""API local para el editor de revisión. Corre en tu propia máquina, sin servidor externo."""

import re
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.paths import PROJECTS_DIR, OUTPUT_DIR, DATA_DIR
from core.pipeline import translate_file
from core.project_store import ProjectStore
from core.models import UnitStatus
from core.translation_memory import TranslationMemory
from core.registry import PARSERS, get_parser

LANGUAGES = {"es", "en", "fr", "de", "it", "pt", "ja", "ko"}

# Los archivos que subes desde el editor se guardan en data/uploads/ (carpeta ignorada por Git)
UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Trabajos de traducción en curso o terminados (viven en memoria mientras el servidor esté encendido)
JOBS: dict[str, dict] = {}

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


class ApproveAllRequest(BaseModel):
    overrides: dict[str, str] = {}  # ediciones sin aprobar: id de unidad -> texto


def project_file(name: str) -> str:
    """Convierte el nombre de un proyecto en su ruta, validando que no pueda salirse de projects/."""
    if not re.fullmatch(r"[\w\- ]+", name):
        raise HTTPException(status_code=400, detail="Nombre de proyecto inválido")
    path = PROJECTS_DIR / f"{name}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return path.as_posix()


@app.get("/formats")
def list_formats():
    return sorted(PARSERS.keys())


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


@app.post("/projects/{name}/approve-all")
def approve_all(name: str, body: ApproveAllRequest):
    path = project_file(name)
    project = ProjectStore.load(path)
    memory = TranslationMemory()

    approved = 0
    for unit in project.units:
        if unit.id in body.overrides:
            unit.translated_text = body.overrides[unit.id]
            memory.store(unit.source_text, unit.translated_text, project.source_lang, project.target_lang)
        if unit.translated_text and unit.status != UnitStatus.APPROVED:
            unit.status = UnitStatus.APPROVED
            approved += 1

    ProjectStore.save(project, path)
    return {"approved": approved, "units": [u.model_dump() for u in project.units]}


@app.post("/projects/{name}/export")
def export_project(name: str):
    project = ProjectStore.load(project_file(name))
    extension = project.original_path.rsplit(".", 1)[-1]
    parser = get_parser(extension)

    output_path = (OUTPUT_DIR / f"{name}_translated.{extension}").as_posix()
    parser.export(project.units, project.original_path, output_path)

    return {"output_path": output_path}


def unique_name(stem: str, extension: str) -> str:
    """Busca un nombre libre tanto en data/uploads/ como en projects/."""
    name, n = stem, 2
    while (UPLOADS_DIR / f"{name}.{extension}").exists() or (PROJECTS_DIR / f"{name}.json").exists():
        name = f"{stem}_{n}"
        n += 1
    return name


def run_translation(job_id: str, input_path: str, project_name: str, source_lang: str, target_lang: str):
    job = JOBS[job_id]

    def on_progress(done: int, total: int):
        job["done"] = done
        job["total"] = total

    try:
        project_path = (PROJECTS_DIR / f"{project_name}.json").as_posix()
        translate_file(input_path, project_path, source_lang, target_lang, on_progress=on_progress)
        job["status"] = "done"
    except Exception as e:  # por ejemplo: clave de DeepL ausente o cuota agotada
        job["status"] = "error"
        job["error"] = str(e)


@app.post("/translate")
async def start_translation(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    source_lang: str = Form(...),
    target_lang: str = Form(...),
):
    if source_lang not in LANGUAGES or target_lang not in LANGUAGES:
        raise HTTPException(status_code=400, detail="Idioma no soportado")
    if source_lang == target_lang:
        raise HTTPException(status_code=400, detail="El idioma de origen y el de destino son el mismo")

    original = Path(file.filename or "").name
    extension = Path(original).suffix.lstrip(".").lower()
    if extension not in PARSERS:
        formats = ", ".join(f".{f}" for f in sorted(PARSERS))
        raise HTTPException(status_code=400, detail=f"Formato no soportado (.{extension}). Formatos disponibles: {formats}")

    stem = re.sub(r"[^\w\- ]", "_", Path(original).stem).strip() or "proyecto"
    name = unique_name(stem, extension)

    input_path = UPLOADS_DIR / f"{name}.{extension}"
    input_path.write_bytes(await file.read())

    job_id = uuid.uuid4().hex
    JOBS[job_id] = {"status": "running", "done": 0, "total": 0, "project": name, "error": None}
    background_tasks.add_task(run_translation, job_id, input_path.as_posix(), name, source_lang, target_lang)

    return {"job_id": job_id, "project": name}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    return job