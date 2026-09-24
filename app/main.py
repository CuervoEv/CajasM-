from fastapi import FastAPI, File, HTTPException, Query, UploadFile

from app.nomenclatura import parse_nomenclatura
from app.pdf_service import pdf_to_images

app = FastAPI(title="PDF a imagen")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/convert")
async def convert(
    file: list[UploadFile] = File(...),
    dpi: int = Query(150, ge=36, le=300, description="Resolución de las imágenes"),
    formato: str = Query("jpeg", description="jpeg (más liviano) o png"),
    calidad: int = Query(95, ge=10, le=100, description="Calidad JPEG 10-100"),
):
    """Recibe 1 o más PDFs. Solo procesa los que cumplan la nomenclatura."""
    if not file:
        raise HTTPException(status_code=400, detail="Debes enviar al menos un PDF")

    pdfs = []
    rechazados = []

    for upload in file:
        nombre = upload.filename or "sin_nombre.pdf"
        meta = parse_nomenclatura(nombre)

        if meta is None:
            rechazados.append(
                {
                    "nombre_pdf": nombre,
                    "motivo": "No cumple nomenclatura: CAJA MENOR - <PLANTA> - <CCDC>.pdf (CCDC máx. 6)",
                }
            )
            await upload.read()
            continue

        if not nombre.lower().endswith(".pdf"):
            rechazados.append({"nombre_pdf": nombre, "motivo": "No es un PDF"})
            await upload.read()
            continue

        pdf_bytes = await upload.read()
        if not pdf_bytes:
            rechazados.append({"nombre_pdf": nombre, "motivo": "Archivo vacío"})
            continue

        try:
            imagenes = pdf_to_images(
                pdf_bytes, dpi=dpi, formato=formato, calidad=calidad
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error al convertir {nombre}: {e}"
            ) from e

        pdfs.append(
            {
                "nombre_pdf": meta["nombre_pdf"],
                "planta": meta["planta"],
                "ccdc": meta["ccdc"],
                "count": len(imagenes),
                "imagenes": imagenes,
            }
        )

    if not pdfs and rechazados:
        raise HTTPException(
            status_code=400,
            detail={
                "mensaje": "Ningún PDF cumple la nomenclatura",
                "rechazados": rechazados,
            },
        )

    return {
        "count": len(pdfs),
        "pdfs": pdfs,
        "rechazados": rechazados,
    }
