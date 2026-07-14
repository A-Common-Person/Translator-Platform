"""Modelo del glosario: pares término-original → término-traducido, por proyecto."""

from pydantic import BaseModel, Field


class GlossaryEntry(BaseModel):
    source_term: str
    target_term: str


class Glossary(BaseModel):
    id: str
    name: str
    source_lang: str
    target_lang: str
    entries: list[GlossaryEntry] = Field(default_factory=list)

    def as_dict(self) -> dict[str, str]:
        return {e.source_term: e.target_term for e in self.entries}