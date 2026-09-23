# Checklist admin VPS (n8n en Docker)

## 1. Cargar la imagen

```bash
docker load < pdf-a-png-1.0.tar.gz
docker images | grep pdf-a-png
```

Debe aparecer `pdf-a-png` tag `1.0`.

## 2. Misma red que n8n

```bash
docker ps --format '{{.Names}}' | grep -i n8n
docker inspect NOMBRE_CONTENEDOR_N8N --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}'
```

Anota el nombre de la red (ej. `n8n_default`, `n8n_network`).

## 3. Levantar el microservicio

Opción A — `docker run`:

```bash
docker run -d \
  --name pdf-a-png \
  --restart unless-stopped \
  --network NOMBRE_RED_N8N \
  --memory 1g \
  pdf-a-png:1.0
```

Opción B — [`docker-compose.yml`](../docker-compose.yml) en la raíz del repo:
comenta `ports`, descomenta `networks` / `n8n_network` y ajusta el nombre de la red.

```bash
docker compose up -d
```

Opción C — snippet [`docker-compose.snippet.yml`](docker-compose.snippet.yml) añadido al compose de n8n.

**No es obligatorio** mapear `-p 8000:8000` si solo n8n lo consume por red interna.

## 4. Verificar

```bash
docker run --rm --network NOMBRE_RED_N8N curlimages/curl:latest \
  http://pdf-a-png:8000/health
```

Esperado: `{"status":"ok"}`

## 5. Configurar el nodo HTTP Request en n8n

- Method: `POST`
- URL: **`http://pdf-a-png:8000/convert`**
- Body Content Type: Form-Data / Multipart
- Parámetro: Name = `file`, Type = Binary File, Input Data Field Name = el binary del PDF (suele ser `data`)
- Timeout: aumentar (ej. 120000 ms o más) para PDFs grandes
- **No usar** `http://localhost:8000` ni `host.docker.internal` en el VPS

## 6. Seguridad y recursos

- Preferible **no** exponer el puerto 8000 al firewall público.
- Memoria recomendada del contenedor: **≥ 1 GB** (PDFs ~11 MB + rasterización).
- Nomenclatura de archivos aceptada: `CAJA MENOR - <PLANTA> - dd-mm-aaaa.pdf`

## 7. Actualizar versión

```bash
docker rm -f pdf-a-png
docker load < pdf-a-png-X.Y.tar.gz
# volver a docker run / compose up
```
