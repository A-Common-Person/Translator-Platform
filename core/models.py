"""Modelo de datos común. Todo formato de entrada se normaliza a TranslatableUnit."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class UnitStatus(str, Enum):
    PENDING = "pending"
    MACHINE_TRANSLATED = "machine_translated"
    REVIEWED = "reviewed"
    APPROVED = "approved"


class Position(BaseModel):
    x: int
    y: int
    width: int
    height: int
    reading_order: int


class TranslatableUnit(BaseModel):
    id: str
    source_text: str
    translated_text: Optional[str] = None
    context: Optional[str] = None
    position: Optional[Position] = None
    status: UnitStatus = UnitStatus.PENDING
    metadata: dict = Field(default_factory=dict)


class Project(BaseModel):
    id: str
    name: str
    source_lang: str
    target_lang: str
    units: list[TranslatableUnit] = Field(default_factory=list)
    