"""Memoria de traducción: reutiliza traducciones ya hechas para el mismo texto exacto."""

import sqlite3


class TranslationMemory:
    def __init__(self, db_path: str = "translation_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    source_text TEXT NOT NULL,
                    source_lang TEXT NOT NULL,
                    target_lang TEXT NOT NULL,
                    translated_text TEXT NOT NULL,
                    PRIMARY KEY (source_text, source_lang, target_lang)
                )
            """)

    def lookup(self, source_text: str, source_lang: str, target_lang: str) -> str | None:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT translated_text FROM memory WHERE source_text = ? AND source_lang = ? AND target_lang = ?",
                (source_text, source_lang, target_lang),
            ).fetchone()
        return row[0] if row else None

    def store(self, source_text: str, translated_text: str, source_lang: str, target_lang: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO memory (source_text, source_lang, target_lang, translated_text)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(source_text, source_lang, target_lang)
                   DO UPDATE SET translated_text = excluded.translated_text""",
                (source_text, source_lang, target_lang, translated_text),
            )