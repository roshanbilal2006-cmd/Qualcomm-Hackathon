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

## 3. Missing Sensor Coordinates

```
missing latitude/longitude
   ↓
backend/pipeline/orchestrator.py
   ↓
correlate_sensor_data()
   ↓
correlation boolean gate fails
   ↓
noise_db/pm25/pm10 values do not become physically correlated evidence
   ↓
scoring visible in development_score
```

When sensor latitude or longitude fields are absent, the pipeline now leaves those coordinate values missing and correlation returns `False` instead of inventing a geographic match from a hardcoded location.

## 4. AI fallback

```
AI service unavailable
   ↓
backend/adapters/ai_adapter.py
   ↓
explicit unknown visual result default
   ↓
orchestrator pipeline stores Unknown stage/progress/confidence
   ↓
empty embedding list means embedding unavailable
   ↓
back-end scoring and output
```

If the AI service is not reachable, the adapter returns a provider-neutral `description` string (`Current AI service unavailable; visual construction evidence was not verified.`) and an `embedding: []` payload. This does not fabricate an AI vector or impersonate any provider such as OpenRouter.
