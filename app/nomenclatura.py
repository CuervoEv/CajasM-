import re
from pathlib import PurePosixPath

# SOPORTE CJM <PLANTA>.pdf — el nombre (sin extensión) debe ir en mayúsculas
NOMENCLATURA = re.compile(r"^SOPORTE CJM (.+)$")


def parse_nomenclatura(nombre: str) -> dict | None:
    """Valida: SOPORTE CJM <PLANTA>.pdf (nombre en mayúsculas)."""
    nombre = nombre.strip()
    nombre = nombre.replace("\\", "/").rsplit("/", 1)[-1]

    path = PurePosixPath(nombre)
    if path.suffix.lower() != ".pdf":
        return None

    stem = path.stem
    if stem != stem.upper():
        return None

    match = NOMENCLATURA.match(stem)
    if not match:
        return None

    planta = match.group(1).strip()
    if not planta:
        return None

    return {
        "nombre_pdf": nombre,
        "planta": planta,
    }
