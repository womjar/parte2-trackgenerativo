# Microservicio de Análisis de Flakiness de Runs de Testing

Este proyecto implementa un micro-servicio REST (con FastAPI) que recibe la información de un **run de pruebas** en formato JSON y devuelve:

- `p_flaky`: probabilidad de flakiness (0–1).
- `priority`: prioridad (`high` / `medium` / `low`).
- `recommendation`: recomendación corta (≤ 40 palabras) para el equipo de QA.

Todo está pensado para ejecutarse en **Docker**: tanto el servicio como los tests se corren dentro del contenedor.


**1. Tecnologías principales**

- **Python 3.12**
- **FastAPI** para el microservicio REST.
- **Pydantic v2** para validación y tipado de la entrada/salida.
- **Uvicorn** como servidor ASGI.
- **Pytest** para los tests unitarios.
- **Docker** para empaquetado y ejecución.



**2. Arquitectura del proyecto**

Estructura de carpetas:

```text

  ├─ app/
  │  ├─ __init__.py
  │  ├─ main.py         # Define la API (FastAPI) y el endpoint /analyze
  │  ├─ models.py       # Modelos Pydantic para request/response
  │  └─ service.py      # Lógica de negocio y heurística de flakiness
  ├─ tests/
  │  └─ test_analyze_endpoint.py  # Tests unitarios del endpoint /analyze
  ├─ requirements.txt
  └─ Dockerfile


3. API REST


  Endpoint principal

  POST /analyze

  Request (JSON)

  Ejemplo:


  {
    "release_cycle": "RC-20250328",
    "platform": "android",
    "environment": "test_app",
    "device_id": "Any_Samsung",
    "test_suite": "regression",
    "scenarios_total": 50,
    "scenarios_failed": 4,
    "duration_sec": 3120,
    "retries": 1,
    "diff_size": 344,
    "usage_cpu": 0.47,
    "memory_mb": 812.3
  }

  Ejemplo Response (JSON):


  {
    "p_flaky": 0.76,
    "priority": "high",
    "recommendation": "Ejecutar en paralelo para confirmar flakiness, revisar logs de escenarios intermitentes y fijar dependencias del entorno antes del próximo release."
  }



4. Ejecución con Docker (servicio)


- Construir la imagen

    docker build -t parte2-trackgenerativo .


- Levantar el microservicio para el microservicio REST.

    docker run -d -p 8000:8000 --name flaky_service parte2-trackgenerativo


- Ejecutar todos los tests

    docker run --rm parte2-trackgenerativo pytest
