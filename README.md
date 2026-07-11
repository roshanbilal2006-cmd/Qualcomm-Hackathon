# LandSense AI

Multi-device construction intelligence platform powered by Snapdragon AI.

This branch, `AI-VLM`, is the current integration branch for the hackathon build. It contains the backend orchestration layer, cloud/community layer, laptop-side AI/VLM image processing boundary, IoT simulator, MCP/RERA simulator, and web dashboard.

The intended product flow is simple:

```text
Android phone captures photos + GPS
        |
        v
Laptop backend receives the scan
        |
        v
Laptop AI service preprocesses/analyzes images
        |
        v
Backend fuses AI + RERA + IoT + cloud/history context
        |
        v
Cloud stores processed community observations
        |
        v
Android displays report + heatmap + nearby history
```

Android should not run heavy AI inference for this version. The phone only captures inputs and displays outputs. Image preprocessing/inference lives on the laptop AI service in `ai/`.

## What Is Built

- FastAPI backend orchestrator on port `8000`.
- Laptop-side AI service on port `8001`.
- AI image engine in `ai/engine.py` that decodes Base64/data URL images, extracts OpenCV visual features, uses OpenRouter vision for construction stage/progress/confidence when `OPENROUTER_API_KEY` is configured, and returns embeddings.
- IoT/Arduino simulator on port `8002`.
- Cloud/community intelligence service on port `8003`.
- MCP/RERA simulator on port `8004`.
- Static web dashboard on port `8080`.
- SQLite local database with seeded RERA/demo projects.
- Backend-to-cloud sync for processed observations.
- Heatmap and history APIs.
- Correlation logic for matching camera scans with sensor readings.
- Development score logic with explainable summary output.
- Imported IoT + MCP REST data layer at the repository root, with mock RERA data,
  demo sensor readings, and a serial Arduino adapter for live hackathon hardware.

## What Is Still Missing

### Android App

The real Android app is still the main missing client piece.

It must:

- Capture 1-4 construction-site photos.
- Capture GPS latitude/longitude.
- Attach UTC timestamp.
- Compress/resize images before upload.
- Convert images to Base64 or `data:image/jpeg;base64,...`.
- Send the scan to the laptop backend at `POST /observation`.
- Display the returned construction report.
- Fetch `/heatmap` and render other users' processed observations.
- Fetch `/history` for the current user/device.
- Show sensor readings from other users with date/time where available.
- Let demo users configure the laptop backend IP address.

### OpenRouter VLM

The laptop AI service now uses OpenRouter as the primary VLM and OpenCV as the local visual preprocessing/guardrail layer. Set `OPENROUTER_API_KEY` in `.env` and choose a vision-capable model with `OPENROUTER_VISION_MODEL`. If the key or API is unavailable, the service falls back to OpenCV-only analysis while preserving the same backend contract.

### Real MCP

The MCP simulator exists, but the active backend pipeline still uses local SQLite RERA records for nearby project lookup. The next integration step is to route RERA/project lookups through `backend.adapters.mcp_adapter.MCPAdapter` with SQLite as fallback.

### Real IoT

The Arduino UNO Q path is simulated. Real dust/noise hardware should expose the same telemetry shape as `GET /sensor`.

## Branch Commands

Use these commands to switch to and inspect the integration branch.

```bash
git fetch origin
git switch AI-VLM
```

If the local branch does not exist yet:

```bash
git switch --track origin/AI-VLM
```

Check branch status:

```bash
git status --short --branch
git log --oneline --decorate -8
```

See what changed against the backend/cloud branch:

```bash
git diff --stat cloud+backend...AI-VLM
```

List project files:

```bash
rg --files
```

## Run and Check Everything

Install dependencies:

```bash
pip install -r requirements.txt
```

Compile-check Python files:

```bash
python -m compileall backend ai cloud iot mcp scripts
```

Start all local services:

```bash
python scripts/run_all.py
```

Service URLs:

```text
Backend:       http://localhost:8000
AI service:    http://localhost:8001
IoT service:   http://localhost:8002
Cloud service: http://localhost:8003
MCP service:   http://localhost:8004
Dashboard:     http://localhost:8080
```

Check backend:

```bash
curl http://localhost:8000/health
```

Check AI service:

```bash
curl http://localhost:8001/health
```

Run a simulated scan:

```bash
python scripts/simulate_scan.py
```

Run backend/cloud integration test:

```bash
python scripts/test_backend_cloud_integration.py
```

## Imported IoT + MCP REST Service

The `mcp+IoT` branch is integrated as a root-level FastAPI service. It exposes a
stable sensor/RERA contract through `main.py`, `routes/`, `services/`,
`adapters/`, `interfaces/`, `models/`, `config/`, and `data/mock_rera.json`.

Run it directly when you want to test that service by itself:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8010
```

Useful endpoints:

```text
GET /status
GET /sensor
GET /rera
GET /nearby_projects
GET /project/{id}
```

By default it uses demo/mock mode from `.env.example`: `SENSOR_MODE=demo` and
`RERA_MODE=mock`. Mock RERA data is stored in `data/mock_rera.json`. To use a
real Arduino, set `SENSOR_MODE=live` and configure `ARDUINO_PORT` for the
machine, for example `COM3` on Windows.

## Android Input Contract

Android sends only capture data to the laptop backend.

Endpoint:

```text
POST http://<LAPTOP_IP>:8000/observation
```

Required fields:

- `timestamp`: UTC ISO 8601 string.
- `latitude`: phone GPS latitude.
- `longitude`: phone GPS longitude.
- `images`: Base64 image strings or `data:image/jpeg;base64,...` strings.

Optional fields:

- `owner_id`: local user/device/session ID for private history filtering.
- `voice_query`: optional text or voice-to-text query.
- `noise_db`, `dust_pm25`, `dust_pm10`, `sensor_timestamp`: optional device-supplied sensor values. Android does not need these for the first version.

Example request:

```json
{
  "timestamp": "2026-07-09T10:30:00Z",
  "owner_id": "android-demo-device-001",
  "latitude": 12.9716,
  "longitude": 77.7500,
  "images": [
    "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ..."
  ],
  "voice_query": "Check whether this construction site is active."
}
```

## Backend Output Contract

Example response:

```json
{
  "observation_id": "uuid-string",
  "timestamp": "2026-07-09T10:30:00Z",
  "latitude": 12.9716,
  "longitude": 77.7500,
  "images": [],
  "voice_query": "Check whether this construction site is active.",
  "construction_stage": "Structural Work",
  "confidence": 0.88,
  "progress": 55.0,
  "noise_db": 74.2,
  "dust_pm25": 38.5,
  "dust_pm10": 79.1,
  "sensor_status": "connected",
  "rera_projects": [
    {
      "name": "Prestige Kings County",
      "builder": "Prestige Group",
      "status": "Approved",
      "distance": 120.5
    }
  ],
  "development_score": 80.0,
  "summary": "Structural Work is estimated at 55% progress. Nearby verified RERA approval (+15 pts).",
  "embedding": [0.01, 0.02, 0.03]
}
```

Android should show:

- Construction stage.
- Progress percentage.
- Confidence.
- Development score.
- Summary.
- Sensor status.
- Noise dB.
- Dust PM2.5 and PM10.
- RERA/project matches.
- Observation ID.
- Timestamp.
- GPS coordinates.

If a value is `null`, show `Unavailable`.

## Heatmap and History for Android

Backend health:

```text
GET http://<LAPTOP_IP>:8000/health
```

Current user's history:

```text
GET http://<LAPTOP_IP>:8000/history?owner_id=<OWNER_ID>
```

Public heatmap:

```text
GET http://<LAPTOP_IP>:8000/heatmap
```

Nearby local RERA/demo projects:

```text
GET http://<LAPTOP_IP>:8000/nearby?latitude=12.9716&longitude=77.7500&radius=500
```

Heatmap points can be colored by `development_score`:

- `0-30`: low activity.
- `31-60`: medium activity.
- `61-100`: high activity.

## Current Architecture

```text
Android App
  CameraX photos
  GPS coordinates
  UTC timestamp
  optional query
        |
        | POST /observation
        v
Backend Orchestrator
  validates ObservationInput
  creates observation ID
  calls AIAdapter
        |
        v
AI Service
  decodes Base64/data URL image
  resizes image
  extracts visual features
  estimates stage/progress/confidence
  returns embedding
        |
        v
Backend Fusion Pipeline
  gets IoT telemetry
  correlates by time and distance
  gets nearby RERA records
  calculates development score
  writes local SQLite history
  sends processed data to cloud
        |
        v
Cloud Community Layer
  stores observations
  serves heatmap
  serves history/latest sensor data
        |
        v
Android App
  displays report
  displays heatmap/history
```

## Android Implementation Notes

Recommended stack:

- Kotlin.
- CameraX.
- FusedLocationProviderClient.
- Retrofit or Ktor client.
- Coroutines.
- Simple MVVM.

Image handling:

- Resize longest side to around 1024 px.
- JPEG quality around 70-80.
- Encode as `data:image/jpeg;base64,...`.
- Start with one image; support up to four images later.

Network notes:

- Phone and laptop must be on the same Wi-Fi.
- Android must use the laptop LAN IP, not `localhost`.
- Example: `http://192.168.1.10:8000`.

Rules:

- Android talks only to backend.
- Android must not call AI, IoT, MCP, or cloud services directly.
- Raw images go to laptop backend/AI only.
- Cloud receives processed observations, not raw images.

## Project Structure

```text
ai/
  engine.py            Laptop-side image preprocessing/inference boundary
  main.py              AI FastAPI service

backend/
  api/                 Backend REST routes
  adapters/            AI, IoT, MCP, cloud adapters
  database/            SQLite setup and RERA seed data
  fusion/              Correlation and scoring
  models/              Pydantic and SQLAlchemy models
  pipeline/            Observation orchestration

cloud/                 Community history, heatmap, latest sensor, chat hooks
iot/                   Arduino telemetry simulator
mcp/                   MCP/RERA simulator
web/                   Browser demo dashboard
scripts/               Run/test/demo helpers
docs/                  Architecture and API docs
```

## Known Cleanup Items

- `android-app/local.properties` is machine-specific and should not be committed.
- `cloud_data.db` may appear as an untracked local runtime database.
- The AI engine is OpenRouter + OpenCV. Without `OPENROUTER_API_KEY`, prediction still works in OpenCV fallback mode but cloud VLM reasoning is disabled.
- Invalid Android images currently fall back to mock AI output through the adapter; for production, invalid images should return a clear validation error.

