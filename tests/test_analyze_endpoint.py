from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _base_payload():
    return {
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
        "memory_mb": 812.3,
    }


def test_analyze_returns_expected_schema():
    payload = _base_payload()
    response = client.post("/analyze", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "p_flaky" in data
    assert "priority" in data
    assert "recommendation" in data

    assert 0.0 <= data["p_flaky"] <= 1.0
    assert data["priority"] in {"high", "medium", "low"}
    assert isinstance(data["recommendation"], str)
    assert len(data["recommendation"].split()) <= 40


def test_high_flakiness_run_has_high_priority():
    payload = _base_payload()
    payload["scenarios_failed"] = 20  # 40% de fallos
    payload["retries"] = 2
    response = client.post("/analyze", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["priority"] == "high"
    assert data["p_flaky"] >= 0.4  # al menos razonablemente alta


def test_low_flakiness_run_has_low_or_medium_priority():
    payload = _base_payload()
    payload["scenarios_failed"] = 0
    payload["retries"] = 0
    payload["diff_size"] = 10
    payload["usage_cpu"] = 0.1
    payload["memory_mb"] = 256.0

    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["priority"] in {"low", "medium"}
    assert data["p_flaky"] <= 0.6


def test_invalid_scenarios_failed_greater_than_total():
    payload = _base_payload()
    payload["scenarios_failed"] = 999  # mayor que total

    response = client.post("/analyze", json=payload)
    # Pydantic lanza error de validación -> 422
    assert response.status_code == 422
