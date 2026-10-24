"""Etapa 1 desde la terminal: traducir un archivo y guardar el proyecto para revisión."""

import sys

from core.pipeline import translate_file

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Uso: python translate.py <archivo_entrada> <proyecto.json> <idioma_origen> <idioma_destino>")
        sys.exit(1)
    translate_file(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])