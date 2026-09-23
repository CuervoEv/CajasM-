import re

# CAJA MENOR - <PLANTA> - dd-mm-aaaa.pdf
NOMENCLATURA = re.compile(
    r"^CAJA MENOR - (.+?) - (\d{2}-\d{2}-\d{4})\.pdf$",
    re.IGNORECASE,
)


def parse_nomenclatura(nombre: str) -> dict | None:
    """Valida el nombre del PDF. Devuelve planta y fecha, o None si no cumple."""
    nombre = nombre.strip()
    # Quitar ruta si viene incluida
    nombre = nombre.replace("\\", "/").rsplit("/", 1)[-1]

    match = NOMENCLATURA.match(nombre)
    if not match:
        return None

    return {
        "nombre_pdf": nombre,
        "planta": match.group(1).strip(),
        "fecha": match.group(2),
    }
