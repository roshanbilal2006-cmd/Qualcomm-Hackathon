# System Architecture

LandSense AI uses the Snapdragon X Elite laptop as the local edge brain. Android captures field data, the laptop performs image analysis and orchestration, and the cloud layer stores processed community observations for heatmaps and history.

## Device Roles

| Device/service | Responsibility |
| --- | --- |
| Android phone | Capture photos, GPS, timestamp, optional query; display report, heatmap, history |
| Backend on laptop | Main orchestrator; receives scans, calls AI/IoT/MCP/cloud, stores local history |
| AI service on laptop | Decodes and preprocesses images; estimates construction stage/progress/confidence |
| IoT/Arduino | Provides dust/noise telemetry |
| MCP/RERA | Provides external/local project context |
| Cloud | Stores processed observations; serves heatmap, history, latest sensor/community data |

## Main Flow

```text
Android phone
  Camera photos
  GPS coordinates
  UTC timestamp
  optional text/voice query
        |
        | POST /observation
        v
Backend orchestrator
  validate payload
  create observation ID
  call AI service
        |
        v
AI service
  decode Base64/data URL image
  resize/preprocess image
  extract visual features
  estimate construction stage
  return progress/confidence/embedding
        |
        v
Backend fusion pipeline
  request IoT telemetry
  correlate sensor reading by time and distance
  query local RERA/MCP context
  compute development score
  write local SQLite history
  sync processed observation to cloud
        |
        v
Cloud community layer
  store processed observation
  serve heatmap/history/latest sensor data
        |
        v
Android phone
  display current result
  display public heatmap
  display user history
```

## Android Boundary

Android is a capture and display client.

Android sends:

- `timestamp`
- `owner_id` optional
- `latitude`
- `longitude`
- `images`
- `voice_query` optional

Android receives:

- construction stage
- progress
- confidence
- sensor status
- dust/noise readings
- RERA/project matches
- development score
- summary
- heatmap/history data

Android must not directly call:

- AI service
- IoT service
- MCP service
- Cloud service

All service communication goes through the backend.

## AI Boundary

The AI service is laptop-side. The current `AI-VLM` branch has a deployable heuristic engine in `ai/engine.py`. It accepts Base64/data URL images, preprocesses them with Pillow, extracts visual features, and returns a stable contract.

This is the replacement point for real FastVLM/LiteRT/ONNX inference. The backend adapter should not need to change when the model internals are replaced.

AI service input:

```json
{
  "images": [
    "data:image/jpeg;base64,..."
  ]
}
```

AI service output:

```json
{
  "construction_stage": "Structural Work",
  "progress_percentage": 55,
  "confidence": 0.88,
  "description": "Structural Work is estimated at 55% progress.",
  "embedding": [0.01, 0.02, 0.03]
}
```

The backend adapter normalizes this into:

```json
{
  "stage": "Structural Work",
  "progress": 55.0,
  "confidence": 0.88,
  "description": "Structural Work is estimated at 55% progress.",
  "embedding": [0.01, 0.02, 0.03]
}
```

## Cloud Boundary

The backend sends processed observations to cloud. Raw image data should not be stored in cloud by default.

Cloud stores:

- observation ID
- timestamp
- latitude/longitude
- construction stage
- progress/confidence
- sensor readings if available
- development score
- summary
- embedding

Cloud serves:

- public heatmap
- observation history
- latest shared sensor data
- future grounded assistant responses

## Correlation Rules

Phone and Arduino/sensor observations are fused only when both checks pass:

- Time difference is less than or equal to 30 seconds.
- Distance is less than or equal to 50 meters.

If correlation fails, backend still returns a report, but `sensor_status` remains `degraded` and sensor fields are returned as unavailable.

## Architecture Rules

- Backend is the only orchestrator.
- Android talks only to backend.
- AI, IoT, MCP, and cloud stay behind backend adapters.
- Observation JSON is the shared contract.
- UTC timestamps are used internally.
- Cloud sync uses processed observations, not raw images.
- Services should fail gracefully with degraded output when possible.

