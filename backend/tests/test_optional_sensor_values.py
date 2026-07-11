from backend.fusion.scoring import calculate_development_score


def test_missing_noise_and_dust_are_not_treated_as_zero_readings():
    result = calculate_development_score(
        visual_stage="Structural Work",
        progress=45.0,
        visual_confidence=0.8,
        sensor_status="connected",
        noise_db=None,
        dust_pm25=None,
        dust_pm10=None,
        rera_projects=[
            {
                "name": "Registered Site",
                "builder": "Builder",
                "status": "Approved",
                "distance": 25.0,
            }
        ],
    )

    assert result["development_score"] == 60.0
    assert "noise levels are extremely quiet" not in result["summary"]
    assert "No dust/noise readings were supplied" in result["summary"]


def test_partial_sensor_values_only_use_supplied_metrics():
    result = calculate_development_score(
        visual_stage="Structural Work",
        progress=45.0,
        visual_confidence=0.8,
        sensor_status="connected",
        noise_db=None,
        dust_pm25=120.0,
        dust_pm10=None,
        rera_projects=[],
    )

    assert "extremely quiet" not in result["summary"]
    assert "High noise and dust telemetry" not in result["summary"]
    assert "Environmental warning" in result["summary"]
