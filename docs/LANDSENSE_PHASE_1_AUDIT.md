# 1. Executive Summary

LandSense is a multi-service AI-assisted urban development intelligence repository spanning Android/mobile capture, a backend orchestrator, an AI inference service, an MCP/IoT services layer, cloud observation storage and retrieval, and a static web dashboard. The repository currently contains a real FastAPI service structure, a Python SQLite-backed backend, a cloud service with retrieval and chat APIs, and an AI service that prefers a Qualcomm NPU local engine and falls back to a vision/OpenCV-based inference engine. The main RERA and sensor data surfaces are partially mock-driven and default to a demo/mock configuration. The system is best understood as a repository-level prototype baseline rather than a production-ready deployment.

# 2. Repository Structure

Important repository areas:

- `ai/`: AI service and inference engines.
- `ai/models/fastvlm/`: FastVLM model artifacts documentation.
- `ai/models/vlm/`: VLM notebook and model documentation.
- `backend/`: Orchestrator service, API routes, SQLite model/domain definitions, scoring/fusion logic.
- `cloud/`: Community intelligence service storing heatmap/history/sensor/chat endpoints.
- `mcp/`: MCP service with IoT sensor adapters, RERA adapters, project/status routes, and mock data.
- `mobile/`: Android Kotlin/Compose app sources.
- `web/`: Static dashboard HTML/CSS/JS.
- `scripts/`: Demo and test scripts for service orchestration and specimen data.
- `docs/`: Architecture, API contract, API docs, and setup notes.

# 3. Current Architecture

Actual architecture visible from repository code:

```
USER / MOBILE APP
   ↓
POST /observation to backend service
   ↓
backend.main -> backend.api.routes -> backend.pipeline.orchestrator
   ↓
AI service at http://localhost:8001/health and /predict
   ↓
MCP service at mcp.main for sensor and RERA/project/status
   ↓
Cloud service at cloud.main for storage, heatmap, history, sensor, stats, chat
   ↓
SQLite local DB in backend and cloud database
   ↓
Static web dashboard and Android UI
```

Known current implementation details:

- AI service uses `SnapdragonVisionEngine` if available. If not loaded, it falls back to `VisionInferenceEngine` in `ai/engine.py`.
- `VisionInferenceEngine` has an OpenCV scene feature extractor and optional OpenRouter integration in configuration.
- Backend includes `backend/pipeline/orchestrator.py` for score fusion and route handling.
- MCP service builds mock or live sensor and RERA adapters through `mcp/adapters/factory.py`.
- Cloud service stores observations via `cloud/services/retrieval_service.py` and uses `LLMService` for chat.

# 4. End-to-End User Flow

Actual current flow that is implemented in the repository:

1. User opens Android/web dashboard or hits backend endpoints.
2. Mobile/app or demo request submits an observation payload containing timestamp, latitude, longitude, images, optional voice query, and optional sensor values.
3. Backend receives payload at `backend/api/routes.py` and stores an observation or forwards pipeline workflow to score and reasoning.
4. AI service receives image frames and returns structured image/scene analysis. Report in `ai/engine.py` gives progress/stage/confidence constrains.
5. Sensor values may be passed from backend or project context. In the MCP module, sensor adapters can emit random/dummy readings or a real serial adapter for Arduino-style hardware when configured.
6. RERA/project context is served by `MockRERAAdapter` under default configuration by reading `mcp/data/mock_rera.json`.
7. Backend scoring and fusion logic combines sensor inputs, RERA context, visuals, and image processing features.
8. Cloud endpoints store and retrieve heatmap, history, stats, chat context and latest sensor conditions.
9. UI is static or Android app view layer, showing report, chat, and dashboard.

# 5. Component Inventory

| Component | Location | Status | Real/Mock | Notes |
| --- | --- | --- | --- | --- |
| AI Service | `ai/main.py` | Implemented | Partially real | FastAPI AI service with NPU-first and OpenCV/OpenRouter fallback |
| AI Engine | `ai/engine.py` | Implemented | Partially real | Uses OpenCV features and image decode parser |
| NPU Engine | `ai/npu_engine.py` | Implemented | Partially real | SnapdragonVisionEngine; loads only if artifacts exist |
| Backend Orchestrator | `backend/main.py` and `backend/api/routes.py` | Implemented | Real | Main local API layer |
| Scoring/Fusion | `backend/fusion/scoring.py` | Implemented | Real rules | Rule-based development scoring |
| DB Session | `backend/database/session.py` | Implemented | Real | SQLite setup |
| Cloud Service | `cloud/main.py` | Implemented | Real API surface | Observation storage and chat endpoints |
| MCP Service | `mcp/main.py` | Implemented | Mostly real framework | sensor + RERA + project adapters |
| Sensor Adapters | `mcp/adapters/sensor/*` | Implemented | Mixed | Dummy random generation, live path exists |
| RERA Adapters | `mcp/adapters/rera/*` | Implemented | Mixed | Mock default, live adapter possible |
| Web Dashboard | `web/` | Implemented | Real static UI | HTML/CSS/JS |
| Android App | `mobile/app/src/` | Implemented | Real UI | Kotlin app |
| Scripts | `scripts/` | Implemented | Demo/test | Run-once scripts |

# 6. Data Source Inventory

| Data | Source | Real/Mock | Entry Point | Consumer |
| --- | --- | --- | --- | --- |
| Image | Mobile app or HTTP observation payload | Real but optional in test/demo | `backend/api/routes.py`, `ai.engine` | AI service and scoring |
| GPS | Observation payload, backend routes | Real payload contract | `backend/api/routes.py` | Backend, cloud, scoring, correlation |
| Timestamp | Observation payload, generated by device/request | Real payload contract | API route or test scripts | DB, scoring, sensor correlation |
| Noise | MCP sensor adapter; default `dummy_sensor_adapter.py` | Mock/random | `mcp.services.sensor_service` | Backend and cloud structure |
| PM2.5 / PM10 | MCP sensor adapter; default `dummy_sensor_adapter.py` | Mock/random | `mcp.services.sensor_service` | Backend and cloud structure |
| RERA/Project | `mcp/data/mock_rera.json`, `MockRERAAdapter` | Mock | `mcp/adapters/rera/mock_rera_adapter.py` | Backend and MCP routes |
| Cloud history | SQLite in cloud service | Real local storage | `cloud/database.py` | Retrieval and chat |
| Local session DB | `backend/database/session.py` | Real SQLite | backend | Dashboard/report |

# 7. Fake/Mock/Hardcoded Data Inventory

| File | Function | Data | Type | Downstream Impact |
| --- | --- | --- | --- | --- |
| `mcp/data/mock_rera.json` | `MockRERAAdapter` | RERA records | Static/mock JSON | Provides default project context |
| `mcp/adapters/rera/mock_rera_adapter.py` | `MockRERAAdapter` | Project/location records | Fake dataset | Feeds routes and project status |
| `mcp/adapters/sensor/dummy_sensor_adapter.py` | `DummySensorAdapter` | Random bounded sensor readings | Random/dummy | Creates noise, PM2.5, PM10 fields |
| `mcp/config/settings.py` | `get_settings` defaults | `RERA_MODE=mock`; `SENSOR_MODE=demo` | Hardcoded default | Routes operate in mock mode by default |
| `ai/engine.py` | `VisionInferenceEngine` | Prompt/scene/sentence construction | Rule-based fallback | Fallback AI output is deterministic and synthetic |

# 8. AI Implementation Audit

Current provider:

- AI service in `ai/main.py` first probes `SnapdragonVisionEngine`, which attempts `npu_engine` and logs on likely device and runtime systems.
- If that engine reports `not loaded`, the service instantiates `VisionInferenceEngine` from `ai/engine.py`.

Provider/model:

- NPU engine is represented by `SnapdragonVisionEngine` and `ai/model` artifacts.
- VLM/OpenCV fallback is the `VisionInferenceEngine` in `ai/engine.py`.
- The `VisionInferenceEngine` uses OpenCV and an `OpenRouter` style path in the health endpoint output.

Endpoint:

- `POST /predict` in `ai/main.py` receives `images: list[str]`.
- `GET/POST /health` reports engine and model status.

Request format:

- JSON object with `images` list of base64/data-image strings.

Response format:

- Structured output object from the engine, including `stage`, `progress`, `confidence`, `summary`, `ai_backend`, and `inference_source`.

Error handling:

- `ImageDecodeError` is caught in `predict()` and converted to an error response.

Fallback:

- Implementation prefers NPU engine, then OpenCV fallback. No Ollama is present in the current repository.

Caching:

- Not detected in current repository.

Structured output:

- Present as a consistent structured dictionary in `VisionInferenceEngine` and `SnapdragonVisionEngine` outputs.

# 9. Sensor Implementation Audit

The repository describes sensor ingestion through `mcp` adapters and route services. Current code:

- `mcp/adapters/sensor/dummy_sensor_adapter.py` generates bounded random values using `random.uniform` for `noise_db`, `pm25`, and `pm10`.
- `mcp/config/settings.py` and `.env` default `SENSOR_MODE=demo` and `RERA_MODE=mock`.
- `mcp/services/status_service.py` reports `sensor_mode` and `rera_mode` as `demo` or `mock` by default.
- `mcp/adapters/factory.py` chooses provider wiring for sensor and RERA; actual sensor provider classes include `DummySensorAdapter` and potential real serial hardware adapters.

Known path:

- `SENSOR_MODE=demo` generates sensor readings.
- `SENSOR_MODE=live` is described but not strongly confirmed in the repository as fully connected. `Arduino` related functions are available as paths but not always complete.

# 10. GPS and Timestamp Audit

GPS and timestamp are received by the backend in request observations. A typical request object includes `timestamp`, `latitude`, `longitude`, `images`, and optional query fields. The API contract in `docs/API_CONTRACT.md` outlines this payload; `backend/api/routes.py` and `backend/models/domain.py` carry the observation shapes. GPS is stored as latitude/longitude across observation tables. Timestamps are stored in the observation record and are also used in sensor request sync use. The repository does not show an independent GPS capture service in the repo; GPS is treated as input payload. This is a configured integration contract rather than a verified physical device integration.

# 11. Project/RERA Data Audit

Project data and RERA information currently come from MCP project/RERA provider machinery. Default configuration intentionally points to `RERA_MODE=mock` and uses `mcp/data/mock_rera.json`. This route is loaded by `mcp/adapters/rera/mock_rera_adapter.py`. The adapter serves records such as project name, status, builder, distance, and nearby context. In `mcp/config/settings.py`, the default `RERA_MODE` is `mock`. A live adapter/interface exists, but the repository default is mock and static. Therefore current project data is mock or demo-backed rather than a verified live RERA data source.

# 12. Current Scoring Logic

The backend scoring logic is in `backend/fusion/scoring.py`. The currently implemented scoring is rule-based and uses thresholds and conditions such as:

- high noise and dust indicate active development;
- mismatch between visual construction progress and quiet sensors reduces confidence;
- site-likelihood and progress stage produce a development score;
- `visual_construction` and `confidence` statuses feed the reasoning summary.

The implementation is deterministic and rule-driven. It does not include a training model or probability model. It is partially connected to the backend observation route. The exact scoring output is derived from a structured rule combination rather than a learned model.

# 13. Spatial/Temporal Correlation

Repository correlation logic exists in `backend/fusion/scoring.py`, `mcp/services/status_service.py`, and `cloud/services/retrieval_service.py`. Spatial and temporal correlations are conceptual and partial:

- GPS is stored by observation and consumed by `cloud.get_nearby` and `get_history` endpoints.
- MCP sensor and project sources can be correlated by the route or service layer.
- No strong repository-wide verified distance or time-difference policy such as `distance < 50m` or `time difference < 30 seconds` is found in the code by static inspection.
- `distance` values come from mock dataset records, and RERA routes parse them.

# 14. Database/Storage

The repository uses multiple storage surfaces:

- Backend uses `backend/database/session.py` and `backend/models/db.py` for the local SQLite dataset.
- Cloud uses `cloud/database.py` and `cloud/models.py` to persist observations and retrieval results.
- MCP service uses route/service abstraction with data in memory or sample JSON files.

Storage is local SQLite and cloud SQLite-like file-backed fast storage. No strong transaction/locking or conflict resolution layer is visible.

# 15. Offline Capability

Offline capability is partially documented in the repository but not confirmed with runtime evidence. AI service can load a local NPU engine when artifacts are available. `ai/main.py` reports a fallback path if the NPU engine is not loaded. However, the repository does not provide a verified end-to-end local-only execution path for sensor, GPS, image, scoring, and cloud sync. `Ollama` and other local LLM agents are not present as actual service wiring in the repository.

# 16. Security Findings

Static inspection shows an `mcp/.env` with sample settings including `RERA_MODE=mock` and `MOCK_RERA_DATA_PATH`. A secret/API credential detection rule should be triggered if private keys or tokens are committed. In the static code and docs audited here, no actual API credential values were printed. `mcp/.env` and `.env.example` are present and should be moved to secure configuration if they contain real credentials. Do not include actual secret values in any report. Passive security findings: `allow_origins=["*"]` in backend CORS middleware is permissive; the repository uses `FastAPI` and no detailed authentication layer is present.

# 17. Dependencies

Major dependencies include FastAPI, Uvicorn, SQLAlchemy, Pydantic, scipy/OpenCV, `dotenv`, and optional numpy/torch-like packages. These are declared in the top-level and service requirements files. Duplicate or optional dependencies appear across `requirements.txt`, `cloud/requirements.txt`, and `mcp/requirements.txt`. The dependency stack is layered and not fully normalized.

# 18. Dead/Unused/Experimental Code

The repository contains notebooks, experimental model artifacts, old model documentation, and unused fallback pathways. The AI service supports engines and model rollback. `mobile` app code, `web` dashboard, `ai/models/vlm/notebook.ipynb`, and `ai/models/fastvlm/README.md` appear to be packaging or demo/experimental artifacts. Static inspection suggests multiple adapters and old engine paths exist.

# 19. Known Bugs

- Load ordering and backend service startup are sensitive to environment and package path.
- OpenRouter and cloud fallback can degrade or fail if environment variables or credentials are absent.
- The default mock RERA and dummy sensor configuration means no real local sensor or RERA verification path is active by default.
- `mcp/adapters/factory.py` may choose provider classes without a robust health check or validation path.
- Service-specific health loops and loops in scripts assume a specific OS path and environment.

# 20. Incomplete Features

- Verified live RERA integration not active by default.
- Verified real hardware sensor integration not active by default.
- Verified cloud AI provider integration not active by default.
- Full authenticated user/project flow not implemented.
- Offline fallback to Ollama native model is not implemented.
- End-to-end production-grade history and sync are not fully verified.

# 21. Patent-Relevant Technical Components

The repository already contains technical mechanisms that may later deserve investigation, but this audit does not claim novelty.

- Multi-source data collection: Already implemented.
- Image analysis: Already implemented.
- Sensor correlation: Partially implemented.
- Spatial validation: Partially implemented.
- Temporal validation: Partially implemented.
- Confidence: Already implemented in scoring/AI response shape.
- Evidence fusion: Partially implemented.
- Offline processing: Partially implemented.
- Cloud/local inference continuity: Partially implemented.

# 22. Recommended Replacement/Implementation Order

1. Add an inventory of verified components and remove unsupported assumptions.
2. Convert default provider configuration to a documented real or mock profile.
3. Stabilize the backend and cloud route path through endpoint health checks.
4. Separate mock and live adapter wiring with a single settings source.
5. Replace the dummy sensor path with a verified adapter in a controlled phase.
6. Move RERA dataset behavior behind a clearly labeled and testable live adapter.
7. Introduce production readiness checks for AI provider fallback.
8. Document and test offline mode intentionally rather than with UI-only messaging.

# 23. Phase-1 Conclusion

The repository contains a useful but incomplete multi-service baseline that can serve as a Phase-1 audit artifact. It is not yet production-ready. It relies on mock RERA and dummy sensor data by default, uses a rule-based scoring engine and OpenCV/NPU-first AI fallback path, and indicates the future path to cloud/local AI integration without directly implementing that future architecture. The repository can be audited, but it is not a final mature LandSense platform.

---

This document represents a static code audit artifact for the repository in its present state. It intentionally avoids unverified runtime claims and does not claim patent novelty.
