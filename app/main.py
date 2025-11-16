from fastapi import FastAPI

from .models import RunInput, AnalysisOutput
from .service import analyze_run

app = FastAPI(
    title="Flaky Run Analyzer",
    version="1.0.0",
    description=(
        "Micro-servicio REST para estimar la probabilidad de flakiness en runs de testing")
)


@app.post("/analyze", response_model=AnalysisOutput)
def analyze(run: RunInput) -> AnalysisOutput:
    """
    Analiza un run de pruebas y devuelve:

    - p_flaky: probabilidad estimada de flakiness (0-1).
    - priority: high / medium / low.
    - recommendation: recomendación corta (≤ 40 palabras).
    """
    return analyze_run(run)
