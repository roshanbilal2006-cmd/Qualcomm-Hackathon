# System Architecture Specification

This document details the multi-device orchestration architecture of the LandSense AI platform.

## Communication Topology

LandSense AI uses a centralized hub-and-spoke model where the local FastAPI server running on the Snapdragon X Elite Laptop acts as the "Brain".

```
                     OnePlus 15
                 (Camera + GPS + Voice)
                         │
                         ▼
                  Android App
                         │
                         ▼
                REST API (Backend)
                         │
                         ▼
              Observation Pipeline
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
    AI Service      IoT + MCP         SQLite
   FastVLM 0.5B    Sensors + RERA     Demo Data
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                 Fusion Engine
                         │
                         ▼
               Development Report
                         │
                         ▼
                    Cloud Layer
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
        Heatmap                 History DB
```

### Communication Rules
* **Android** connects **ONLY** to the **Backend**.
* **Backend** orchestrates **all** other modules (AI, IoT, SQLite, MCP, Cloud).
* **Direct connections are strictly forbidden**:
  - Android → Cloud (Forbidden)
  - Android → Arduino (Forbidden)
  - Android → AI Service (Forbidden)
  - Cloud → AI Service (Forbidden)
  - Arduino → Cloud (Forbidden)

## Correlation Engine Rules

Since the OnePlus 15 and Arduino IoT node operate independently, the backend must correlate their streams.
The backend correlates sensor readings with camera scans using an observation window:

* **Time Window**: `|Observation Timestamp - Sensor Timestamp| <= 30 seconds`
* **Distance Window**: `Distance(Phone GPS, Sensor GPS) <= 50 meters`

If these conditions are met, the sensor readings (noise, dust pm2.5, dust pm10) are fused into the observation. Otherwise, the sensor readings are ignored, and `sensor_status` is flagged as `disconnected` or `degraded` for that observation.
