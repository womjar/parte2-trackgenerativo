import math

from .models import RunInput, AnalysisOutput


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def compute_p_flaky(run: RunInput) -> float:
    """Modelo heurístico sencillo que estima la probabilidad de flakiness."""

    failure_rate = run.scenarios_failed / run.scenarios_total
    retry_factor = min(run.retries, 3) / 3.0
    diff_factor = min(run.diff_size, 500) / 500.0
    duration_factor = min(run.duration_sec / 3600.0, 2.0) / 2.0  # normalizado hasta 2h
    cpu_factor = run.usage_cpu  # ya normalizado 0-1
    mem_factor = min(run.memory_mb / 2048.0, 1.0)  # cap en 2GB

    # Pesos elegidos heurísticamente: doy más importancia al failure_rate
    z = (
        -1.2
        + 3.0 * failure_rate
        + 1.5 * retry_factor
        + 1.2 * diff_factor
        + 0.8 * duration_factor
        + 0.5 * cpu_factor
        + 0.3 * mem_factor
    )

    p = _sigmoid(z)
    # Ajuste de seguridad para evitar 0/1 exactos por temas numéricos
    return max(0.001, min(0.999, p))


def compute_priority(p_flaky: float, run: RunInput) -> str:
    failure_rate = run.scenarios_failed / run.scenarios_total

    if p_flaky >= 0.7 or (failure_rate >= 0.2 and run.retries > 0):
        return "high"
    elif p_flaky >= 0.4:
        return "medium"
    else:
        return "low"


def build_recommendation(p_flaky: float, priority: str, run: RunInput) -> str:
    """Genera una recomendación de ≤ 40 palabras basada en el contexto del run."""
    failure_rate = run.scenarios_failed / run.scenarios_total

    if priority == "high":
        if run.retries > 0:
            rec = (
                "Revisar escenarios intermitentes, analizar logs del run y "
                "fijar datos dependientes del entorno. Ejecutar la suite en "
                "dos tipos de dispositivo para confirmar flakiness."
            )
        elif run.diff_size > 300:
            rec = (
                "El cambio fue grande. Dividir la suite en grupos pequeños, "
                "añadir aserciones más específicas y monitorear los casos "
                "fallidos en runs consecutivos."
            )
        else:
            rec = (
                "Priorizar análisis de los escenarios fallidos, habilitar "
                "logging detallado y ejecutar el run varias veces en paralelo "
                "para confirmar comportamiento flaky."
            )
    elif priority == "medium":
        if failure_rate > 0.1:
            rec = (
                "Revisar dependencias externas, tiempos de espera y uso de "
                "recursos. Etiquetar los tests sospechosos y ejecutar un "
                "subconjunto crítico en cada build."
            )
        else:
            rec = (
                "Monitorear los escenarios fallidos en los siguientes "
                "releases, agregando métricas de estabilidad por test y "
                "alertas cuando se repitan fallos en el mismo caso."
            )
    else:  # low
        rec = (
            "Mantener monitoreo básico de la suite y registrar historial de "
            "flakiness por escenario. No es necesario interrumpir el ciclo "
            "de release, pero revisar si aparecen patrones recurrentes."
        )

    # Asegurar máximo 40 palabras
    words = rec.split()
    if len(words) > 40:
        rec = " ".join(words[:40])
    return rec


def analyze_run(run: RunInput) -> AnalysisOutput:
    p_flaky = compute_p_flaky(run)
    priority = compute_priority(p_flaky, run)
    recommendation = build_recommendation(p_flaky, priority, run)

    return AnalysisOutput(
        p_flaky=round(p_flaky, 2),
        priority=priority,
        recommendation=recommendation,
    )
