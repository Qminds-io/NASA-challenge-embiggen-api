
# NASA Embiggen API

Backend FastAPI para un visor privado de capas planetarias. Mantiene un pipeline simple: esquemas Pydantic -> servicios -> repositorios -> clientes externos, sin capas extra.

## Que ofrece
- Catalogo de capas agrupado por cuerpo usando respuestas camelCase.
- Proxy WMTS hacia NASA GIBS y Solar System Treks con cache en disco y encabezados Cache-Control/ETag.
- Anotaciones globales estilo Google Maps (lat/lon, titulos, metadata) persistidas en PostgreSQL.
- Control de origen y rate limiting (120 solicitudes/min por IP en endpoints que golpean la base de datos).
- Servicios dedicados (`services/layers.py`, `services/annotations.py`, `services/tiles.py`).

## Estructura rapida
- `app/schemas.py`: modelos Pydantic para requests/responses.
- `app/services/`: logica por feature.
- `app/repositories/`: consultas SQLAlchemy por modelo.
- `app/broadcast/nasa.py`: cliente HTTP reutilizable para GIBS/Treks con cache (`app/cache.py`).
- `app/db/`: configuracion SQLAlchemy (base, session, modelos, migraciones Alembic).
- `app/api/routes/`: routers FastAPI (`/v1/layers`, `/v1/annotations`, `/v1/layers/{layer}/tiles`).
- `tests/`: pruebas unitarias e integracion.

## Requisitos
- Python 3.9 o superior.
- SQLite por defecto (seleccionable via `APP_DATABASE_URL`).
- Dependencias listadas en `requirements.txt`.

## Puesta en marcha
1. Crear y activar un entorno virtual: `python -m venv .venv` y `source .venv/bin/activate` (Windows ` .\.venv\Scripts\activate`).
2. Instalar paquetes: `pip install -r requirements.txt`.
3. Copiar `.env.example` a `.env` y ajustar valores (puedes definir `APP_DATABASE_URL` completo o bien `APP_DB_USER`, `APP_DB_PASSWORD`, `APP_DB_HOST`, `APP_DB_PORT`, `APP_DB_NAME`).
   - En docker-compose se levanta un contenedor Postgres (puerto 5433 externo) con credenciales `nasa/nasa` para replicar produccion.
   - En App Runner mapea las subclaves de los secretos `rds!db-45b2301c-91f2-4157-9bcc-c09cd0c8c42b` (username/password) y `nasa-YjR1sP` (host/port/dbname) a las variables `APP_DB_*`.
4. Ejecutar migraciones: `alembic upgrade head`.
5. Iniciar el servidor: `uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload`.

## Seguridad
- Solo se aceptan solicitudes cuyo encabezado Origin coincide con los dominios configurados en `APP_ALLOWED_ORIGINS` (por defecto https://embiggen.example.com). Las rutas internas de documentacion (`/docs`, `/redoc`, `/openapi.json`) y peticiones sin encabezado Origin siempre se permiten.
- Las rutas que impactan base de datos estan limitadas a 120 solicitudes por minuto por direccion IP.
- Para eliminar anotaciones se requiere el codigo secreto configurado en `APP_ANNOTATION_DELETE_SECRET` (por defecto `qminds`).

## API Reference

Todas las peticiones deben incluir el encabezado `Origin` con un dominio permitido.

### GET /api/health
- **Descripcion:** Verifica la disponibilidad del servicio.
- **Response 200:**
```json
{
  "status": "ok"
}
```

### GET /v1/layers
- **Descripcion:** Retorna el catalogo de capas agrupado por cuerpo celeste.
- **Response 200:** estructura camelCase con listas de capas por cuerpo.

### GET /v1/layers/{layer_key}/tiles/{z}/{x}/{y}
- **Descripcion:** Proxy de teselas NASA.
- **Query opcional:** `date=YYYY-MM-DD` (requerida para capas GIBS cuando no hay `defaultDate`).
- **Response 200:** Cuerpo binario con la imagen del tile. Encabezados relevantes: `Content-Type`, `Cache-Control`, `ETag`, `Last-Modified`.

### GET /v1/annotations
- **Descripcion:** Lista anotaciones globales. Puede filtrarse por bounding box.
- **Query opcional:** `swLat`, `swLon`, `neLat`, `neLon` (double) para delimitar la vista.
- **Response 200 (ejemplo):**
```json
{
  "items": [
    {
      "id": 1,
      "lat": -34.6,
      "lon": -58.45,
      "title": "Buenos Aires",
      "description": "Capital",
      "properties": {"color": "red"},
      "createdAt": "2024-05-10T12:00:00Z",
      "updatedAt": "2024-05-10T12:00:00Z"
    }
  ]
}
```

### POST /v1/annotations
- **Descripcion:** Crea anotaciones globales en lote.
- **Request body:**
```json
{
  "frame": {
    "layerKey": "gibs:MODIS_Terra_CorrectedReflectance_TrueColor",
    "date": "2024-05-12",
    "projection": "EPSG:3857",
    "zoom": 4.3,
    "opacity": 0.75,
    "center": {"lon": -58.45, "lat": -34.6},
    "extent": {"minLon": -70.12, "minLat": -42.3, "maxLon": -46.8, "maxLat": -27.1}
  },
  "features": [
    {
      "id": "tmp-123",
      "order": 0,
      "feature": {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-58.45, -34.6]},
        "properties": {"name": "Buenos Aires"}
      },
      "properties": {"color": "#FF0000"}
    }
  ]
}
```
- **Response 201:**
```json
{
  "frame": { ... },
  "features": [ { "id": "1", "order": 0, ... } ]
}
```

### POST /v1/annotations/query
- **Descripcion:** Devuelve las anotaciones dentro del frame suministrado.
- **Request body:** mismo formato que `POST /v1/annotations`, las `features` pueden omitirse.
- **Response 200:**
```json
{
  "frame": { ... },
  "features": [ { "id": "1", "order": 0, ... } ]
}
```

### DELETE /v1/annotations/{annotation_id}
- **Descripcion:** Elimina un marcador global (requiere query `secret=qminds`, o el valor definido en `APP_ANNOTATION_DELETE_SECRET`).
- **Response 200:**
```json
{
  "status": "deleted"
}
```

### Errores comunes
- `403 origin_not_allowed`: el encabezado `Origin` no coincide con los dominios autorizados.
- `429 rate_limited`: se excedio el limite de 120 solicitudes por minuto.
- `404 layer_not_found` / `404 annotation_not_found`: recursos inexistentes.
- `502/504` en el proxy de tiles cuando la API de NASA falla.

## Testing
```
python -m pytest
```
Incluye pruebas para el broadcast NASA (mock via `respx`) y anotaciones globales sobre SQLite en memoria.

## Siguientes pasos sugeridos
1. Generar migraciones Alembic para las tablas actuales antes de desplegar en entornos compartidos.
2. Cambiar el cache de archivos por Redis u otro backend distribuido si se ejecuta en multiples instancias.
3. Persistir el estado del rate limiting en un almacenamiento centralizado cuando haya varios replicas del servicio.
4. Evaluar reemplazar `on_event` por lifespan en FastAPI para evitar deprecaciones.
