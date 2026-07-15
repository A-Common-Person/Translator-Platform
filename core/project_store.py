"""Guarda y carga el estado de un proyecto de traducción en un archivo JSON."""

import json
from core.models import Project, TranslatableUnit


class ProjectStore:
    @staticmethod
    def save(project: Project, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(project.model_dump_json(indent=2))

    @staticmethod
    def load(path: str) -> Project:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Project(**data)