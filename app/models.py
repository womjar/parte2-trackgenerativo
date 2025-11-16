from typing import Literal

from pydantic import BaseModel, Field, field_validator


class RunInput(BaseModel):
    release_cycle: str
    platform: str
    environment: str
    device_id: str
    test_suite: str

    scenarios_total: int = Field(gt=0, description="Total de escenarios ejecutados")
    scenarios_failed: int = Field(
        ge=0, description="Número de escenarios fallados en el run"
    )
    duration_sec: int = Field(gt=0, description="Duración total del run en segundos")
    retries: int = Field(ge=0, description="Número de reintentos del run")
    diff_size: int = Field(
        ge=0, description="Tamaño del diff del cambio (por ejemplo, líneas de código)"
    )
    usage_cpu: float = Field(
        ge=0.0,
        le=1.0,
        description="Uso promedio de CPU normalizado entre 0 y 1",
    )
    memory_mb: float = Field(gt=0, description="Memoria promedio utilizada en MB")

    @field_validator("scenarios_failed")
    @classmethod
    def validate_failed_scenarios(cls, v: int, info):
        total = info.data.get("scenarios_total")
        if total is not None and v > total:
            raise ValueError("scenarios_failed no puede ser mayor que scenarios_total")
        return v


class AnalysisOutput(BaseModel):
    p_flaky: float = Field(ge=0.0, le=1.0)
    priority: Literal["high", "medium", "low"]
    recommendation: str
