# Translator Platform

> Nombre provisional. Plataforma modular de traducción, pensada para convertirse en un programa instalable que procesa todo de forma local.

Translator Platform traduce contenido de distintos formatos con un flujo de trabajo en el que **tú revisas y corriges** el resultado antes de exportarlo. La traducción automática es un borrador, no el producto final.

## Estado del proyecto

En desarrollo activo. Hoy funciona el flujo completo para texto; los demás frentes están planeados.

| Área                                                           | Estado                 |
| -------------------------------------------------------------- | ---------------------- |
| Libros y texto (TXT, EPUB)                                     | Funcionando            |
| Traducción con DeepL (API gratuita)                            | Funcionando            |
| Glosarios (consistencia de nombres y términos)                 | Funcionando            |
| Memoria de traducción (SQLite, local)                          | Funcionando            |
| Editor de revisión web (local)                                 | Funcionando, en mejora |
| Diálogos de videojuegos (JSON/CSV, luego RPG Maker `.rvdata2`) | Planeado               |
| OCR y traducción sobre imagen (manga/manhwa)                   | Planeado               |
| Empaquetado como programa instalable                           | Planeado               |

## Cómo funciona

El flujo se divide en tres etapas independientes:

1. **Traducir**: se lee el archivo, se traduce cada unidad de texto (usando memoria y glosario) y se guarda un proyecto de revisión.
2. **Revisar**: se abre el proyecto en el editor para aprobar o corregir cada traducción. Las correcciones alimentan la memoria de traducción.
3. **Exportar**: se genera el archivo final en su formato original con las traducciones revisadas. No hace falta aprobar todas las unidades: las que no revisaste salen con la traducción automática.

### Arquitectura

Todo formato de entrada se convierte a una misma estructura interna (`TranslatableUnit`), por lo que el motor de traducción, el glosario, la memoria y el editor sirven para cualquier formato.

- **Parsers** (`parsers/`): un plugin por formato; implementan `parse` y `export`. Se registran con el decorador `@register_parser`.
- **Proveedores** (`providers/`): un plugin por motor de traducción; implementan `translate`. Hoy: DeepL (y un proveedor mock para pruebas).
- **Núcleo** (`core/`): modelos de datos, interfaces, registro de plugins, glosario, memoria de traducción, almacenamiento de proyectos y rutas de carpetas.
- **API** (`api/`): backend local con FastAPI que alimenta el editor.
- **Editor** (`editor-web/`): interfaz web que corre en tu propia máquina.

## Requisitos

- Python 3.13 (probado en Windows con PowerShell y VS Code)
- Una clave de la API gratuita de DeepL (plan "Developer", no requiere tarjeta)

## Instalación

```powershell
git clone https://github.com/A-Common-Person/Translator-Platform.git
cd Translator-Platform

python -m venv venv
venv\Scripts\Activate.ps1

pip install pydantic deepl python-dotenv ebooklib beautifulsoup4 fastapi "uvicorn[standard]"
```

> En Windows usa `python` y no `python3`: este último puede apuntar al lanzador de Microsoft Store en lugar de tu entorno virtual.

### Configuración

Crea un archivo `.env` en la raíz del proyecto con tu clave de DeepL:

```
DEEPL_API_KEY=tu-clave-aqui:fx
```

El archivo `.env` ya está en `.gitignore`. No compartas tu clave ni la subas al repositorio.

## Uso

Corre siempre los comandos **desde la raíz del repositorio**, con el entorno virtual activado. Las carpetas de trabajo (`samples/`, `output/`, `projects/` y `data/`) se crean solas la primera vez.

Si pasas solo un nombre de archivo, cada script lo busca o lo guarda en la carpeta que le corresponde. Si pasas una ruta con carpeta, se respeta tal cual.

### 1. Traducir

```powershell
python translate.py <archivo_entrada> <proyecto.json> <idioma_origen> <idioma_destino>

# Ejemplo: de inglés a español (lee samples/sample.epub, guarda projects/proyecto.json)
python translate.py sample.epub proyecto.json en es
```

### 2. Revisar

Con el editor web (recomendado). El editor abre el proyecto `projects/proyecto.json`:

```powershell
uvicorn api.main:app
```

Después abre `editor-web/index.html` en tu navegador (doble clic o `start editor-web\index.html`). Desde ahí puedes corregir y aprobar unidades, filtrar las pendientes y exportar el archivo final a `output/exported.epub`. Una corrección solo se guarda al pulsar **Aprobar**.

> Para desarrollar con reinicio automático puedes usar `--reload`, pero conviene limitarlo a tus carpetas de código para que no vigile `venv/`:
> `uvicorn api.main:app --reload --reload-dir api --reload-dir core --reload-dir parsers --reload-dir providers`

O desde la terminal:

```powershell
python review.py proyecto.json
```

### 3. Exportar

```powershell
# Guarda el resultado en output/libro_traducido.epub
python export_project.py proyecto.json libro_traducido.epub
```

## Estructura del repositorio

```
Translator-Platform/
├── core/              # modelos, interfaces, registro, glosario, memoria, rutas
├── parsers/           # txt_parser.py, epub_parser.py
├── providers/         # deepl_provider.py, mock_provider.py
├── api/               # backend local (FastAPI)
├── editor-web/        # editor de revisión (HTML/JS)
├── samples/           # archivos de entrada de ejemplo
├── translate.py       # etapa 1: traducir
├── review.py          # etapa 2: revisar (terminal)
├── export_project.py  # etapa 3: exportar
└── main.py            # flujo directo de una sola pasada (demo)
```

Estas carpetas se generan en tu máquina y **no se suben al repositorio**:

- `projects/`: proyectos de revisión (`.json`)
- `output/`: archivos traducidos y exportados
- `data/`: memoria de traducción (`translation_memory.db`)

## Limitaciones conocidas

- **EPUB**: la tabla de contenidos no se reconstruye al exportar (workaround temporal por un error de `ebooklib`). Solo se traducen párrafos y encabezados (`<p>`, `<h1>`–`<h3>`); el formato en línea dentro de un párrafo (por ejemplo, una palabra en cursiva) se pierde, y el texto que está en otras etiquetas (como el aviso legal de Project Gutenberg, que vive en un `<footer>`) se deja tal cual venía en el original.
- El editor trabaja por ahora con un único proyecto fijo (`projects/proyecto.json`).
- Si editas una traducción en el editor y recargas la página antes de aprobarla, el cambio se pierde.
- La memoria de traducción guarda las traducciones automáticas al generarlas; a futuro solo guardará las aprobadas.

## Hoja de ruta

- [x] Modelo de datos común y arquitectura de plugins
- [x] Parsers TXT y EPUB
- [x] Traducción con DeepL, glosarios y memoria de traducción
- [x] Flujo traducir → revisar → exportar
- [x] Editor web básico (progreso, filtro de pendientes, exportar desde la página)
- [x] Carpetas de trabajo separadas (`samples/`, `output/`, `projects/`, `data/`)
- [ ] Mejoras del editor (selección de proyecto, pulido de interfaz)
- [ ] Parsers de diálogos de videojuegos (JSON, CSV, XLIFF, Ren'Py)
- [ ] Soporte de RPG Maker (`.rvdata2`)
- [ ] OCR, detección de bocadillos y edición sobre imagen para manga/manhwa
- [ ] Empaquetado como aplicación de escritorio instalable
- [ ] Soporte multi-idioma ampliado y proveedores adicionales

## Licencia y uso

Este proyecto se concibe con el siguiente modelo (aún no formalizado en un archivo `LICENSE`):

- **Uso personal**: libre, para proyectos personales.
- **Uso con fines de lucro por parte de individuos**: requiere consultarlo antes con el autor.
- **Empresas**: licencia de pago, al estilo de WinRAR.

Hasta que exista un archivo `LICENSE`, estos términos reflejan la intención del autor y no sustituyen un texto legal.

## Contacto

Para consultas sobre uso comercial, abre un issue en este repositorio.
