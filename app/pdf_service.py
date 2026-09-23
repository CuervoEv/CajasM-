import base64
import io

import fitz
from PIL import Image, ImageOps


def pdf_to_images(
    pdf_bytes: bytes,
    *,
    dpi: int = 150,
    formato: str = "jpeg",
    calidad: int = 95,
) -> list[dict]:
    """
    Convierte cada página a imagen en escala de grises (ideal para facturas B/N).
    Evita cambios de color del JPEG RGB y mantiene contraste alto.
    """
    formato = formato.lower().strip()
    if formato not in {"jpeg", "jpg", "png"}:
        raise ValueError("formato debe ser jpeg o png")
    if formato == "jpg":
        formato = "jpeg"

    ext = "jpg" if formato == "jpeg" else "png"
    mime = "image/jpeg" if formato == "jpeg" else "image/png"

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []

    for i, page in enumerate(doc, start=1):
        # Escala de grises desde el render: sin tintes de color
        pix = page.get_pixmap(dpi=dpi, colorspace=fitz.csGRAY, alpha=False)
        img = Image.frombytes("L", (pix.width, pix.height), pix.samples)

        # Mejora negros/blancos sin inventar color
        img = ImageOps.autocontrast(img, cutoff=1)

        buffer = io.BytesIO()
        if formato == "jpeg":
            img.save(buffer, format="JPEG", quality=calidad, optimize=True)
        else:
            img.save(buffer, format="PNG", optimize=True)

        pages.append(
            {
                "page": i,
                "filename": f"page_{i:03d}.{ext}",
                "mimeType": mime,
                "data": base64.b64encode(buffer.getvalue()).decode("ascii"),
            }
        )

    doc.close()
    return pages
