# 1. Current System Summary

LandSense is currently a multi-service repository with a Python/FastAPI backend, a Python/FastAPI AI service, an MCP service for sensor and RERA project adapters, an SQLite/JSON-oriented storage layer, and a static web/UI surface. The current default configuration is demo/mock oriented, not a verified production/live sensor or live government project integration.

The code creates an explicit architecture with a backend orchestrator that calls an AI adapter and an MCP adapter, then calls a scoring function before persisting an observation.

# 2. Actual AI Provider

The actual AI provider used by the code is the current implementation in `ai/engine.py`.

The provider is:

CURRENT: Cirrascale/AISuite cloud provider via `LLM_BASE_URL` defaulting to `https://aisuite.cirrascale.com/apis/v2`.

This is verified in `ai/engine.py`:

- `self.llm_base_url = os.getenv("LLM_BASE_URL", "https://aisuite.cirrascale.com/apis/v2")`
- `OpenAI(base_url=self.llm_base_url, api_key=self.llm_api_key)`
- `self.runtime_backend = "Cirrascale vision + OpenCV (...)"` when the API key is configured.

The `ai/main.py` health endpoint says `ai_backend` should be `npu_vlm` or `openrouter_opencv`, but that is not canonical. The actual provider used in the AI engine is Cirrascale/AISuite. The text that mentions OpenRouter in `ai/main.py` is a legacy or placeholder label, not an implemented OpenRouter API path.

OpenRouter is NOT CURRENTLY IMPLEMENTED.

Ollama is NOT CURRENTLY IMPLEMENTED.

# 3. Actual Sensor Provider

The actual default sensor mode in `mcp/config/settings.py` is:

- `sensor_mode: Literal["demo", "live"] = "demo"`

The provider factory in `mcp/adapters/factory.py` selects:

- `DummySensorAdapter()` when `sensor_mode == "demo"`
- `ArduinoSensorAdapter(...)` when `sensor_mode == "live"`

This means the default sensor source is DummySensorAdapter and the data is fake/simulated. The dummy adapter does not produce real sensor hardware readings. It generates bounded random values:

- noise_db with `random.uniform(40, 90)`
- pm25 with `random.uniform(10, 100)`
- pm10 with `random.uniform(20, 150)`

Its `get_status()` always returns `"connected"` even though there is no external dependency or physical sensor. Therefore the current system may report `sensor_status = "connected"` even when the values originate from the dummy adapter. This is a critical current-system limitation.

# 4. Actual GPS Sources

The repository has three distinct location paths that should be separated:

A. User / device / site GPS

This is supplied by the observation request payload at the backend API: `latitude`, `longitude`, `timestamp`, and `images`. It is not generated internally by a fixed GPS provider. This remains a request-based source and is validated only by the request contract and observation object.

B. Sensor GPS

The MCP sensor provider returns sensor readings with `device_id`, `timestamp`, `noise_db`, `pm25`, `pm10` only. The dummy adapter has no physical GPS fields. The dummy adapter does not carry a true sensor GPS coordinate. The backend pipeline, however, uses hardcoded fallback legal coordinates when no sensor latitude/longitude fields are present:

- `sensor_lat = sensor_data.get("latitude", 12.9716)`
- `sensor_lon = sensor_data.get("longitude", 77.7500)`

These are hardcoded geographic fallback values in `backend/pipeline/orchestrator.py` and are used in the correlation threshold check. They influence correlation because `correlate_sensor_data()` uses them to compute distance from the site-requested phone coordinates.

C. Project / RERA GPS

RERA project records originate in `mcp/data/mock_rera.json` and `MockRERAAdapter`, which is an in-repo mock dataset. Project records contain approximate project metadata and `distance` field values. They are not verified government data. They are not live RERA source data.

# 5. Actual Timestamp Sources

Timestamp sources in the current repository are mostly request-based and object-based:

- Observation timestamp from the API request: `input_data.timestamp`.
- Sensor timestamp from dummy and Arduino providers: generated on the provider side using UTC ISO string formatting.
- Project/RERA records and database records store `timestamp` as string records, not necessarily an authoritative audit tick.

The correlation function uses `parse_iso_timestamp` to convert timestamps and `time_diff <= 30.0` seconds threshold. This is a static threshold in `backend/fusion/correlation.py` and is hard-coded in the correlation rule.

# 6. Actual RERA/Project Data Sources

Default mode:

- `rera_mode: Literal["mock", "live"] = "mock"` in `mcp/config/settings.py`

Factory route:

- `MockRERAAdapter(data_path=settings.mock_rera_data_path)` when `rera_mode == "mock"`
- `LiveRERAAdapter(...)` when `rera_mode == "live"`

Mock data source in the repository:

- `mcp/data/mock_rera.json`

The live adapter file shows that some implementation remains a stub:

- if `LIVE_RERA_BASE_URL` is absent, `LiveRERAAdapter.get_all()` raises `RERAUnavailableError`
- no verified active government API path is present in code.

Therefore:

- `RERA_MODE=mock` is active and operational as a static local sample dataset.
- `RERA_MODE=live` is configuration-ready or stub-level, not a verified live RERA integration.

# 7. Actual Spatial Correlation

The code contains Haversine formula in `backend/fusion/correlation.py` and the backend pipeline uses it inside `correlate_sensor_data()`.

Thresholds:

- `time_diff <= 30.0` seconds
- `distance <= 50.0` meters

Those are in the current `correlate_sensor_data()` function. The rules are:

1. Parse timestamp of the user observation request.
2. Parse timestamp of the sensor reading.
3. Compute absolute time difference.
4. Compute `haversine_distance()` between phone coordinates and sensor coordinates.
5. Correlate only if time difference is <= 30s and distance is <= 50m.

If no sensor or coordinates are returned, the backend falls back to the hardcoded defaults in the orchestrator, which can create a false positive correlation path.

# 8. Actual Temporal Correlation

Recorded in `correlate_sensor_data()`:

- timestamp difference threshold is exactly `30.0 seconds`
- `parse_iso_timestamp()` is used for both phone and sensor timestamps
- timestamp missing / malformed data is not always fatal; the code attempts a fallback by using `datetime.now(timezone.utc)` in `parse_iso_timestamp()` if conversion fails.

This means the code currently has a basic threshold and fallback but not a strong validation pipeline for all sources.

# 9. Actual Scoring

The current scoring function is in `backend/fusion/scoring.py`. Inputs:

- `visual_stage`
- `progress`
- `visual_confidence`
- `sensor_status`
- `noise_db`
- `dust_pm25`
- `dust_pm10`
- `rera_projects`

The algorithm:

1. Base score = progress.
2. Visual construction presence is checked. If no image is recognized as construction, base score becomes 0.
3. RERA approvals add +15 points when a nearby approved project is found.
4. Unauthorized/disputed status subtracts 30 points.
5. Missing RERA project subtracts 10 points.
6. Sensor data can produce +10 points for high noise and dust; mismatch threshold subtracts 15 if visual progress says active but noise is too low.
7. Environmental hazard thresholds and conditions are directly coded.

The fake sensor data flow can therefore reach the final development score because the `DummySensorAdapter` output feeds the MCP sensor route and then the backend pipeline score path. If the correlations and thresholds pass, the fake values are used for scoring decisions and summary generation.

# 10. Actual Offline Behavior

Offline behavior is currently not a verified full local intelligence environment.

The repository includes an NPU engine file and local AI engine path, but the actual `ai/main.py` still runs a service route that checks for AI path health through a local service. The `AIAdapter` in `backend/adapters/ai_adapter.py` returns a deterministic `Unknown` output if the AI service cannot be reached.

This means:

- local NPU path is partial and environment dependent
- no real Ollama local fallback is implemented
- cloud AI path is needed for full inference in most directions
- image capture and GPS capture are request-driven, not guaranteed to work offline

# 11. Fake Data

Major fake data sources found:

1. DummySensorAdapter in `mcp/adapters/sensor/dummy_sensor_adapter.py`
2. MockRERAAdapter in `mcp/adapters/rera/mock_rera_adapter.py`
3. Hardcoded fallback sensor coordinates from `backend/pipeline/orchestrator.py`
4. Local fallback response from `backend/adapters/ai_adapter.py` returning a generated Unknown output

These outputs are not equally neutral. Some feed scoring, some feed correlation thresholds, some feed sensor status reporting, and some feed UI/report summaries.

# 12. Hardcoded Data

The currently identified hardcoded values include:

- default AI base URL `https://aisuite.cirrascale.com/apis/v2`
- default `SENSOR_MODE=demo` in `mcp/config/settings.py`
- default `RERA_MODE=mock` in `mcp/config/settings.py`
- sensor `latitude=12.9716` and `longitude=77.7500` default fallback coordinates in `backend/pipeline/orchestrator.py`
- RERA mock dataset source file `mcp/data/mock_rera.json`

These are hardcoded in the source and must be treated as current implementation choices, not as a future data architecture.

# 13. Stubs

The repository clearly contains stubs:

- `LiveRERAAdapter` is a stub with environment-coupled behavior and no verified real fetch path.
- `NPU engine` is optional and only loads if `geniex` artifacts and packages are available.
- `AIAdapter` fallback path returns an explicit Unknown visual result when the AI service is down.

# 14. Broken Features

Static inspection shows that the current AI, sensor and RERA route composition is not complete.

- `LiveRERAAdapter` raises an unavailable error unless configured.
- `ArduinoSensorAdapter` requires a serial port and real hardware; the default path is demo/mock.
- OpenRouter is not implemented.
- Ollama is not implemented.
- A local fallback only exists in the bundle of engine layers and not a verified integrated open-source model path.

# 15. Missing Features

- Verified real sensor and RERA integration.
- Verified production readiness of AI cloud and offline fallback.
- Fully implemented evidence consistency engine.
- Fully implemented evidence fusion with reliability.
- Verified observation trust and contradiction detection.

# 16. Security Problems

The repository contains environment/config files and example credentials. These must be moved to secure configuration. No actual secret value is shown here. In the source, credential/secret detection must be treated as an audit issue only, not as a production-safe credential path.

# 17. Future Planned Architecture

Separate the future architecture from the current repository baseline:

CURRENT:

- Cirrascale/AISuite cloud AI provider
- NPU/local Quick engine optionally available
- MCP mock RERA adapter
- DummySensorAdapter
- Hardcoded fallback longitude/latitude in correlation
- Rule-based development scoring

FUTURE:

- OpenRouter primary cloud AI provider
- Ollama local/offline fallback
- Real sensor and project source integration
- Confidence-aware evidence fusion and reliability engine
- Contradiction detection and evidence consistency pipeline
- Trust/observation assessment

# 18. Final Notes

This project is currently a repository that already contains meaningful multi-service wiring and partial AI and scoring flows, but it is not a production-grade or fully verified live source pipeline. It is a legitimate proof-of-concept baseline that later phases can improve, but only if the system is updated from the facts established here.
