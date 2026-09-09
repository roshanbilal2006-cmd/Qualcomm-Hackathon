# Fake Data → User Output Impact

This file traces fake or simulated values through the current code path.

## 1. DummySensorAdapter

```
DummySensorAdapter
   ↓
MCP Sensor Service via mcp/adapters/factory.py
   ↓
Sensor route / sensor provider reads
   ↓
backend/adapters/mcp_adapter.py get_sensor_data()
   ↓
backend/pipeline/orchestrator.py checks correlation
   ↓
calculate_development_score()
   ↓
development_score and summary
   ↓
API response / ObservationResponse
   ↓
UI / cloud / report / history
```

The fake sensor data path uses the `DummySensorAdapter` to generate bounded random values for `noise_db`, `pm25`, and `pm10`. The random values directly feed the scoring threshold interpretation in `calculate_development_score()`:

- high noise and dust indicate active development
- mismatch penalty when visual progress is active but sensors are quiet
- environmental hazard warnings may be raised if high thresholds are exceeded

This means fake data can affect the score calculation, summary, risk classification, and final user-visible output.

## 2. MockRERAAdapter

```
MockRERAAdapter
   ↓
MockRERAAdapter._load() reads local mock_rera.json
   ↓
MCP RERA provider project routes
   ↓
backend/adapters/mcp_adapter.py get_nearby_projects()
   ↓
backend/pipeline/orchestrator.py rera_projects
   ↓
calculate_development_score()
   ↓
development_score and summary
   ↓
API response
```

The mock RERA project data can affect the score by adding +15 for approved nearby project status, subtracting 30 for disputed or unauthorized statuses, and adding warnings when no RERA project exists.

## 3. Hardcoded Sensor Coordinates

```
Hardcoded fallback coordinates 12.9716, 77.7500
   ↓
backend/pipeline/orchestrator.py
   ↓
used by correlate_sensor_data()
   ↓
correlation boolean gate
   ↓
noise_db/pm25/pm10 values become allowed or ignored
   ↓
scoring visible in development_score
```

The fallback coordinates are used when the sensor data lacks latitude/longitude fields. This influences the correlation gate and therefore the downstream scoring path.

## 4. AI fallback

```
AI service unavailable
   ↓
backend/adapters/ai_adapter.py
   ↓
Unknown visual result default
   ↓
orchestrator pipeline stores Unknown stage/progress/confidence
   ↓
back-end scoring and output
```

If the AI service is not reachable, the adapter returns a `description` string from the fallback `OpenRouter/OpenCV AI service unavailable; visual construction evidence was not verified.` That fallback path is a hardcoded output, not a real AI result.
