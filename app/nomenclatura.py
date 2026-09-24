import re

# CAJA MENOR - <PLANTA> - <CCDC>.pdf
# CCDC = código alfanumérico de 1 a 6 caracteres
NOMENCLATURA = re.compile(
    r"^CAJA MENOR - (.+?) - ([A-Za-z0-9]{1,6})\.pdf$",
    re.IGNORECASE,
)


def parse_nomenclatura(nombre: str) -> dict | None:
    """Valida el nombre del PDF. Devuelve planta y ccdc, o None si no cumple."""
    nombre = nombre.strip()
    nombre = nombre.replace("\\", "/").rsplit("/", 1)[-1]

    match = NOMENCLATURA.match(nombre)
    if not match:
        return None

    return {
        "nombre_pdf": nombre,
        "planta": match.group(1).strip(),
        "ccdc": match.group(2),
    }
