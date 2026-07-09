# API Contracts

This document describes the contracts needed by Android, backend, AI, IoT, MCP, and cloud for the `AI-VLM` integration branch.

## Android to Backend

Android posts construction-site scans to the backend.

Endpoint:

```text
POST /observation
```

Required request fields:

- `timestamp`: UTC ISO 8601 string.
- `latitude`: float.
- `longitude`: float.
- `images`: array of Base64 strings or `data:image/jpeg;base64,...` strings.

Optional request fields:

- `owner_id`: Android device/user/session ID.
- `voice_query`: optional text query.
- `noise_db`, `dust_pm25`, `dust_pm10`, `sensor_timestamp`: optional device-supplied sensor data.

Example:

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

Response:

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

## Backend Health

```text
GET /health
```

Response:

```json
{
  "status": "healthy",
  "device": "Snapdragon X Elite Laptop",
  "role": "Orchestration Brain"
}
```

## History

Current user's local history:

```text
GET /history?owner_id=<OWNER_ID>
```

All local history:

```text
GET /history
```

Response is an array of Observation responses.

## Observation Lookup

```text
GET /observation/{observation_id}
```

Response is one Observation response.

## Heatmap

```text
GET /heatmap
```

Response:

```json
[
  {
    "observation_id": "uuid-string",
    "latitude": 12.9716,
    "longitude": 77.7500,
    "development_score": 80.0,
    "noise_db": 74.2,
    "dust_pm25": 38.5,
    "stage": "Structural Work"
  }
]
```

Note: when cloud is available, backend returns cloud heatmap points. If cloud is unavailable, backend falls back to local SQLite observations.

## Nearby RERA/Demo Projects

```text
GET /nearby?latitude=12.9716&longitude=77.7500&radius=500
```

Response:

```json
[
  {
    "name": "Prestige Kings County",
    "builder": "Prestige Group",
    "status": "Approved",
    "distance": 120.5
  }
]
```

## Backend to AI Service

Endpoint:

```text
POST http://localhost:8001/predict
```

Request:

```json
{
  "images": [
    "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ..."
  ]
}
```

Current `AI-VLM` response:

```json
{
  "construction_stage": "Structural Work",
  "progress_percentage": 55,
  "confidence": 0.88,
  "description": "Structural Work is estimated at 55% progress. The image shows active construction cues.",
  "embedding": [0.01, 0.02, 0.03]
}
```

The backend adapter normalizes this before fusion.

AI health:

```text
GET http://localhost:8001/health
```

## Backend to IoT Service

Endpoint:

```text
GET http://localhost:8002/sensor?lat=12.9716&lon=77.7500
```

Response:

```json
{
  "noise_db": 74.2,
  "pm25": 38.5,
  "pm10": 79.1,
  "timestamp": "2026-07-09T10:30:05Z",
  "device_id": "ARDUINO_UNO_Q_WHITEFIELD",
  "latitude": 12.9716,
  "longitude": 77.7500
}
```

## Backend to Cloud Service

Processed observations only:

```text
POST http://localhost:8003/observation
```

Cloud endpoints:

```text
GET http://localhost:8003/history
GET http://localhost:8003/heatmap
GET http://localhost:8003/latest_sensor
POST http://localhost:8003/chat
```

## Backend to MCP Service

Current simulator endpoint:

```text
GET http://localhost:8004/nearby_projects?latitude=12.9716&longitude=77.7500&radius_meters=500
```

Response:

```json
[
  {
    "name": "Prestige Kings County (MCP-verified)",
    "builder": "Prestige Group",
    "status": "Approved",
    "distance": 120.0
  }
]
```

Current caveat: the backend pipeline still uses local SQLite RERA lookup. MCP adapter integration is the next backend task.

